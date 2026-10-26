"""Headless Blender scene for the CFB Wainwright fire terrain (Blender 5 as a Python module).

Usage:
  python scene.py LAYERDIR OUTDIR orbit   [--frames N] [--res 960x540] [--samples 16]
  python scene.py LAYERDIR OUTDIR pov     [--res 1600x900] [--samples 32]
  python scene.py LAYERDIR OUTDIR pano    [--res 2048x1024]

orbit : 3x vertical exaggeration (stated on screen), camera circles the burn
pov   : true scale (1x), camera at 1.7 m eye height on bare earth plus canopy,
        looking toward the 12:17 Landsat fire line
pano  : true-scale 360-degree equirectangular panorama from each POV point

Labels are not drawn in 3D; each render writes the 2D screen position of the
points of interest to a JSON file so labels can be added afterwards.
"""
import sys, os, json, math, argparse
import numpy as np
import bpy, bmesh
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ap = argparse.ArgumentParser()
ap.add_argument('layers'); ap.add_argument('out'); ap.add_argument('mode')
ap.add_argument('--frames', type=int, default=120)
ap.add_argument('--res', default='960x540')
ap.add_argument('--samples', type=int, default=16)
ap.add_argument('--exag', type=float, default=None)
ap.add_argument('--only', default=None, help='POV name filter')
ap.add_argument('--start', type=int, default=0)
ap.add_argument('--end', type=int, default=None)
ap.add_argument('--burn', type=float, default=0.0, help='0 = pre-fire imagery, 1 = burn applied')
ap.add_argument('--fps', type=int, default=24)
ap.add_argument('--prologue', type=int, default=0, help='render N morning frames (camera eases from Range 11 to the fire camera)')
ap.add_argument('--simtime', type=float, default=None, help='fixed clock (minutes) for a still, e.g. 600 = 10:00')
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
L = lambda f: os.path.join(a.layers, f)
P = json.load(open(L('points.json')))
RES = P['grid']['res']
EXAG = a.exag if a.exag is not None else (3.0 if a.mode == 'orbit' else 1.0)
RX, RY = map(int, a.res.split('x'))

height = np.load(L('height.npy'))
canopy = np.load(L('canopy.npy'))
Z0 = float(np.percentile(height, 1))  # scene datum so numbers stay small

# ---------------------------------------------------------------- reset scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene
scn.render.engine = 'CYCLES'
scn.cycles.device = 'CPU'
scn.cycles.samples = a.samples
scn.cycles.use_denoising = True
scn.cycles.max_bounces = 3
scn.render.resolution_x, scn.render.resolution_y = RX, RY
scn.render.resolution_percentage = 100
scn.render.image_settings.file_format = 'PNG'
scn.view_settings.view_transform = 'AgX'
scn.view_settings.look = 'AgX - Base Contrast' if 'AgX - Base Contrast' in [
    i.identifier for i in scn.view_settings.bl_rna.properties['look'].enum_items] else 'None'


def surface(step, with_canopy):
    h = height[::step, ::step].astype(np.float64)
    if with_canopy:
        # canopy as an occluding surface (10 m cells, so stands read as blocks).
        # The observer needs open ground to stand on: clear canopy within 25 m of
        # each POV point. This is an assumption, stated in the render notes.
        from_c = canopy[::step, ::step].astype(np.float64).copy()
        nr, nc = from_c.shape
        yy, xx = np.mgrid[0:nr, 0:nc]
        for v in P['pov'].values():
            cx, cy = v['x'] / (RES * step), nr - 1 - v['y'] / (RES * step)
            from_c[(xx - cx) ** 2 + (yy - cy) ** 2 <= (25 / (RES * step)) ** 2] = 0
        h = h + from_c
    return (h - Z0) * EXAG


def build_terrain(step, with_canopy):
    z = surface(step, with_canopy)
    nr, nc = z.shape
    cell = RES * step
    xs = np.arange(nc) * cell
    ys = (nr - 1 - np.arange(nr)) * cell  # row 0 is north
    X, Y = np.meshgrid(xs, ys)
    verts = np.column_stack([X.ravel(), Y.ravel(), z.ravel()])
    idx = np.arange(nr * nc).reshape(nr, nc)
    faces = np.column_stack([idx[1:, :-1].ravel(), idx[1:, 1:].ravel(),
                             idx[:-1, 1:].ravel(), idx[:-1, :-1].ravel()])
    me = bpy.data.meshes.new('terrain')
    me.vertices.add(len(verts)); me.vertices.foreach_set('co', verts.astype(np.float32).ravel())
    me.loops.add(faces.size); me.loops.foreach_set('vertex_index', faces.astype(np.int32).ravel())
    me.polygons.add(len(faces))
    me.polygons.foreach_set('loop_start', np.arange(0, faces.size, 4, dtype=np.int32))
    me.update(calc_edges=True)
    # UVs straight from map position (texture covers the full grid)
    W, H = P['grid']['w'] * RES, P['grid']['h'] * RES
    uv = me.uv_layers.new(name='map')
    loop_v = faces.ravel()
    uvs = np.column_stack([verts[loop_v, 0] / W, verts[loop_v, 1] / H])
    uv.data.foreach_set('uv', uvs.astype(np.float32).ravel())
    # per-vertex canopy factor so stands of trees read as trees, not as hills
    cf = np.clip(canopy[::step, ::step] / 4.0, 0, 1).astype(np.float32) if with_canopy \
        else np.zeros((nr, nc), np.float32)
    at = me.attributes.new('canopy', 'FLOAT', 'POINT')
    at.data.foreach_set('value', cf.ravel())
    me.shade_smooth() if hasattr(me, 'shade_smooth') else None
    ob = bpy.data.objects.new('terrain', me)
    scn.collection.objects.link(ob)
    ob.data.materials.append(terrain_material())
    return ob


def terrain_material():
    m = bpy.data.materials.new('ground'); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; Lk = nt.links
    bsdf = N['Principled BSDF']; bsdf.inputs['Roughness'].default_value = 1.0
    # grass and soil have almost no sheen; without this, grazing views at eye
    # level mirror the sky and the ground turns blue-grey
    for nm in ('Specular IOR Level', 'Specular'):
        if nm in bsdf.inputs:
            bsdf.inputs[nm].default_value = 0.0
    tc = N.new('ShaderNodeTexImage'); tc.image = bpy.data.images.load(L('pre_tc.png'))
    tc.interpolation = 'Cubic'
    col = tc.outputs['Color']
    if a.burn > 0:
        # burned ground: blend toward charcoal inside the dNBR scar mask
        sc = N.new('ShaderNodeTexImage'); sc.image = bpy.data.images.load(L('scar.png'))
        sc.image.colorspace_settings.name = 'Non-Color'
        mix = N.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'
        Lk.new(col, mix.inputs[6]); mix.inputs[7].default_value = (0.16, 0.14, 0.13, 1)
        f = N.new('ShaderNodeMath'); f.operation = 'MULTIPLY'; f.inputs[1].default_value = a.burn
        Lk.new(sc.outputs['Color'], f.inputs[0]); Lk.new(f.outputs[0], mix.inputs['Factor'])
        col = mix.outputs[2]
    # canopy: mid-October aspen parkland is mostly bare branches, so grey-brown
    att = N.new('ShaderNodeAttribute'); att.attribute_name = 'canopy'
    cm = N.new('ShaderNodeMix'); cm.data_type = 'RGBA'
    Lk.new(att.outputs['Fac'], cm.inputs['Factor']); Lk.new(col, cm.inputs[6])
    cm.inputs[7].default_value = (0.20, 0.17, 0.14, 1)
    col = cm.outputs[2]
    # fine noise so the 10-20 m imagery doesn't read as flat paint at eye level
    tco = N.new('ShaderNodeTexCoord')
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 0.35
    nz.inputs['Detail'].default_value = 6
    Lk.new(tco.outputs['Object'], nz.inputs['Vector'])
    mr = N.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = 0.8
    mr.inputs['To Max'].default_value = 1.15
    Lk.new(nz.outputs['Fac'], mr.inputs['Value'])
    mul = N.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'
    mul.inputs['Factor'].default_value = 1.0
    Lk.new(col, mul.inputs[6]); Lk.new(mr.outputs[0], mul.inputs[7])
    col = mul.outputs[2]
    bump = N.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.25
    Lk.new(nz.outputs['Fac'], bump.inputs['Height']); Lk.new(bump.outputs[0], bsdf.inputs['Normal'])
    if a.mode == 'fire':
        # per-frame fire texture: R = char (0-1), G = active-front glow (0-1)
        fx = N.new('ShaderNodeTexImage'); fx.image = FX['img']; fx.interpolation = 'Linear'
        sep = N.new('ShaderNodeSeparateColor'); Lk.new(fx.outputs['Color'], sep.inputs[0])
        ch = N.new('ShaderNodeMix'); ch.data_type = 'RGBA'
        Lk.new(sep.outputs[0], ch.inputs['Factor']); Lk.new(col, ch.inputs[6])
        ch.inputs[7].default_value = (0.012, 0.009, 0.007, 1)  # charcoal (linear values: dark)
        col = ch.outputs[2]
        uk = N.new('ShaderNodeMix'); uk.data_type = 'RGBA'   # B = burned, timing unknown
        Lk.new(sep.outputs[2], uk.inputs['Factor']); Lk.new(col, uk.inputs[6])
        uk.inputs[7].default_value = (0.07, 0.055, 0.04, 1)
        col = uk.outputs[2]
        fg = N.new('ShaderNodeMix'); fg.data_type = 'RGBA'   # glowing ground takes the flame colour
        Lk.new(sep.outputs[1], fg.inputs['Factor']); Lk.new(col, fg.inputs[6])
        fg.inputs[7].default_value = (0.9, 0.22, 0.02, 1)
        col = fg.outputs[2]
        gl = N.new('ShaderNodeMath'); gl.operation = 'MULTIPLY'; gl.inputs[1].default_value = 3.0
        Lk.new(sep.outputs[1], gl.inputs[0])
        bsdf.inputs['Emission Color'].default_value = (1.0, 0.12, 0.0, 1)
        Lk.new(gl.outputs[0], bsdf.inputs['Emission Strength'])
    Lk.new(col, bsdf.inputs['Base Color'])
    return m


def emissive(name, rgb, strength):
    m = bpy.data.materials.new(name); m.use_nodes = True
    N = m.node_tree.nodes; N.remove(N['Principled BSDF'])
    e = N.new('ShaderNodeEmission'); e.inputs['Color'].default_value = (*rgb, 1)
    e.inputs['Strength'].default_value = strength
    m.node_tree.links.new(e.outputs[0], N['Material Output'].inputs['Surface'])
    return m


def ground_z(x, y, with_canopy=False, peak=False):
    fc = np.clip(x / RES, 0, height.shape[1] - 2)
    fr = np.clip(height.shape[0] - 1 - y / RES, 0, height.shape[0] - 2)
    c, r = int(fc), int(fr); dc, dr = fc - c, fr - r
    blk = height[r:r + 2, c:c + 2] + (canopy[r:r + 2, c:c + 2] if with_canopy else 0)
    if peak:  # highest surrounding vertex: never puts a camera under the mesh
        h = blk.max()
    else:
        h = (blk[0, 0] * (1 - dc) * (1 - dr) + blk[0, 1] * dc * (1 - dr)
             + blk[1, 0] * (1 - dc) * dr + blk[1, 1] * dc * dr)
    return (h - Z0) * EXAG


def add_hotspots(ground_level=False):
    mat = emissive('hot', (1.0, 0.35, 0.05), 25)
    me = bpy.data.meshes.new('hs'); bm = bmesh.new()
    if ground_level:
        # 30 m Landsat pixel shown as a 3 m tall band of flame (scale marker, not a flame model)
        bmesh.ops.create_cube(bm, size=1.0)
    else:
        bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=6, radius=18)
    bm.to_mesh(me); bm.free(); me.materials.append(mat)
    for h in P['hotspots']:
        if h['source'] != 'LANDSAT_NRT':
            continue
        ob = bpy.data.objects.new('hs', me); scn.collection.objects.link(ob)
        if ground_level:
            ob.scale = (24, 24, 3)
            ob.location = (h['x'], h['y'], ground_z(h['x'], h['y']) + 1.5)
        else:
            ob.location = (h['x'], h['y'], ground_z(h['x'], h['y']) + 6)


def add_outline():
    mat = emissive('scarline', (0.95, 0.15, 0.1), 6)
    for ring in P['scar_outline']:
        cu = bpy.data.curves.new('scar', 'CURVE'); cu.dimensions = '3D'
        cu.bevel_depth = 7; sp = cu.splines.new('POLY'); sp.points.add(len(ring) - 1)
        for i, (x, y) in enumerate(ring):
            sp.points[i].co = (x, y, ground_z(x, y) + 4, 1)
        ob = bpy.data.objects.new('scar', cu); ob.data.materials.append(mat)
        scn.collection.objects.link(ob)


def add_pins():
    mat = emissive('pin', (1, 1, 1), 4)
    for k, v in P['pov'].items():
        cu = bpy.data.meshes.new('pin'); bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=6, radius2=6, depth=1)
        bm.to_mesh(cu); bm.free(); cu.materials.append(mat)
        ob = bpy.data.objects.new('pin_' + k, cu); scn.collection.objects.link(ob)
        z = ground_z(v['x'], v['y'])
        ob.scale = (1, 1, 240); ob.location = (v['x'], v['y'], z + 120)


def sun_position(lat, lon, utc_hours, doy):
    # NOAA low-precision solar position, good to ~0.5 degree
    g = 2 * math.pi / 365 * (doy - 1 + (utc_hours - 12) / 24)
    decl = (0.006918 - 0.399912 * math.cos(g) + 0.070257 * math.sin(g) - 0.006758 * math.cos(2 * g)
            + 0.000907 * math.sin(2 * g) - 0.002697 * math.cos(3 * g) + 0.00148 * math.sin(3 * g))
    eqt = 229.18 * (0.000075 + 0.001868 * math.cos(g) - 0.032077 * math.sin(g)
                    - 0.014615 * math.cos(2 * g) - 0.040849 * math.sin(2 * g))
    tst = utc_hours * 60 + eqt + 4 * lon
    ha = math.radians(tst / 4 - 180)
    la = math.radians(lat)
    cz = math.sin(la) * math.sin(decl) + math.cos(la) * math.cos(decl) * math.cos(ha)
    zen = math.acos(cz)
    az = math.degrees(math.atan2(math.sin(ha), math.cos(ha) * math.sin(la) - math.tan(decl) * math.cos(la))) + 180
    return 90 - math.degrees(zen), az % 360


def lighting():
    # Oct 17, 2026, 3:16 p.m. MDT = 21:16 UTC, day 290
    elev, az = sun_position(52.77, -110.92, 21 + 16 / 60, 290)
    w = bpy.data.worlds.new('w'); scn.world = w; w.use_nodes = True
    N = w.node_tree.nodes; bg = N['Background']
    sky = N.new('ShaderNodeTexSky')
    for t in ('MULTIPLE_SCATTERING', 'NISHITA', 'SINGLE_SCATTERING'):
        try:
            sky.sky_type = t; break
        except Exception:
            pass
    try:
        sky.sun_elevation = math.radians(elev)
        sky.sun_rotation = math.radians(90 - az)  # Blender: 0 = +X (east); counter-clockwise
        sky.altitude = 700
        sky.sun_disc = False
    except Exception:
        pass
    w.node_tree.links.new(sky.outputs[0], bg.inputs[0]); bg.inputs[1].default_value = 0.4
    sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 3.2; sun.angle = math.radians(1.5)
    so = bpy.data.objects.new('sun', sun); scn.collection.objects.link(so)
    # light travels FROM the sun: point the lamp's -Z along the direction to the ground
    d = Vector((math.sin(math.radians(az)) * math.cos(math.radians(elev)),
                math.cos(math.radians(az)) * math.cos(math.radians(elev)),
                math.sin(math.radians(elev))))
    so.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
    # light haze so distance reads (Oct 17 had smoke; keep it subtle and neutral)
    return elev, az


def camera(name='cam', lens=35):
    c = bpy.data.cameras.new(name); c.lens = lens; c.clip_start = 0.5; c.clip_end = 60000
    o = bpy.data.objects.new(name, c); scn.collection.objects.link(o); scn.camera = o
    return o


def look_at(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def screen_points(cam):
    out = {}
    pois = {k: (v['x'], v['y'], ground_z(v['x'], v['y'])) for k, v in P['pov'].items()}
    nf = P.get('noon_fire')
    if nf:
        pois['Fire line, 12:17 p.m. (Landsat)'] = (nf['x'], nf['y'], ground_z(nf['x'], nf['y']))
    for k, p in pois.items():
        co = world_to_camera_view(scn, cam, Vector(p))
        if co.z > 0 and 0 <= co.x <= 1 and 0 <= co.y <= 1:
            out[k] = [co.x * RX, (1 - co.y) * RY, co.z]
    return out


def hotspot_screen(cam):
    out = []
    for i, h in enumerate(P['hotspots']):
        if h['source'] != 'LANDSAT_NRT':
            continue
        base = world_to_camera_view(scn, cam, Vector((h['x'], h['y'], ground_z(h['x'], h['y']))))
        top = world_to_camera_view(scn, cam, Vector((h['x'], h['y'], ground_z(h['x'], h['y']) + 3)))
        out.append({'i': i, 'x': base.x * RX, 'y_base': (1 - base.y) * RY, 'y_top': (1 - top.y) * RY,
                    'depth': base.z})
    return out


FX = {}
elev, az = lighting()
meta = {'mode': a.mode, 'exaggeration': EXAG, 'sun_elev': elev, 'sun_az': az,
        'res': [RX, RY], 'datum_m': Z0, 'frames': {}}

if a.mode == 'orbit':
    build_terrain(step=2, with_canopy=False)
    add_hotspots(); add_outline(); add_pins()
    cam = camera(lens=30)
    c = P['scar_centroid']; tgt = Vector((c['x'], c['y'], ground_z(c['x'], c['y'])))
    R, Hc = 5200, 2300
    end = a.end if a.end is not None else a.frames
    for f in range(a.start, end):
        t = f / a.frames
        ang = math.radians(200 + 70 * t)  # sweep from SSW round to the W/NW (the wind side)
        cam.location = (tgt.x + R * math.sin(ang), tgt.y + R * math.cos(ang), tgt.z + Hc)
        look_at(cam, tgt + Vector((0, 0, -500)))
        scn.render.filepath = os.path.join(a.out, f'orbit_{f:04d}.png')
        bpy.ops.render.render(write_still=True)
        meta['frames'][f] = screen_points(cam)
        json.dump(meta, open(os.path.join(a.out, f'orbit_meta_{a.start:04d}.json'), 'w'))
        print('frame', f, flush=True)

elif a.mode in ('pov', 'pano'):
    build_terrain(step=1, with_canopy=True)
    add_hotspots(ground_level=True)
    cam = camera(lens=24)
    if a.mode == 'pano':
        cam.data.type = 'PANO'
        try:
            cam.data.panorama_type = 'EQUIRECTANGULAR'
        except Exception:
            cam.data.cycles.panorama_type = 'EQUIRECTANGULAR'
    nf = P['noon_fire']
    for k, v in P['pov'].items():
        if a.only and a.only.lower() not in k.lower():
            continue
        z = ground_z(v['x'], v['y'], peak=True) + 1.7
        cam.location = (v['x'], v['y'], z)
        tgt = Vector((nf['x'], nf['y'], ground_z(nf['x'], nf['y']) + 1.7))
        if a.mode == 'pano':
            # centre of the panorama faces the noon fire line; horizon level
            d = tgt - cam.location
            yaw = math.atan2(d.x, d.y)
            cam.rotation_euler = (math.radians(90), 0, -yaw)
        else:
            d = tgt - cam.location; d.z = 0
            look_at(cam, cam.location + d.normalized() * 1000 + Vector((0, 0, -8)))
        bearing = (math.degrees(math.atan2(tgt.x - v['x'], tgt.y - v['y'])) + 360) % 360
        dist = math.hypot(tgt.x - v['x'], tgt.y - v['y'])
        slug = k.lower().replace(' ', '')
        scn.render.filepath = os.path.join(a.out, f'{a.mode}_{slug}.png')
        bpy.ops.render.render(write_still=True)
        meta['frames'][k] = {'bearing_to_noon_fire': bearing, 'dist_to_noon_fire_m': dist,
                             'eye_elev_m': z / EXAG + Z0,
                             'screen': screen_points(cam) if a.mode == 'pov' else {},
                             'hotspots_screen': hotspot_screen(cam) if a.mode == 'pov' else []}
        json.dump(meta, open(os.path.join(a.out, f'{a.mode}_meta.json'), 'w'), indent=1)
        print(a.mode, k, f'bearing {bearing:.0f} dist {dist:.0f} m', flush=True)


# ============================================================== fire animation
STORY = [  # (seconds, sim minutes after midnight) - piecewise-linear clock
    (0.0, 12 * 60 + 17), (1.5, 12 * 60 + 17), (5.0, 14 * 60 + 49), (7.0, 15 * 60 + 16),
    (15.0, 15 * 60 + 45), (18.0, 15 * 60 + 45)]
FINAL_FADE = (15.6, 17.0)  # unknown-timing patches and the dNBR scar fade in here


def sim_time(sec):
    for (s0, t0), (s1, t1) in zip(STORY, STORY[1:]):
        if sec <= s1:
            return t0 + (t1 - t0) * (sec - s0) / max(s1 - s0, 1e-9)
    return STORY[-1][1]


if a.mode == 'fire':
    from scipy.ndimage import zoom
    arr = np.load(L('arrival_min.npy')); unk = np.load(L('unknown.npy')); sev = np.load(L('severity.npy'))
    FM = json.load(open(L('fire_meta.json')))
    Hh, Ww = arr.shape
    big = np.where(np.isfinite(arr), arr, 1e5)
    arr5 = zoom(big, 2, order=1)
    scar5 = np.asarray(__import__('PIL.Image', fromlist=['Image']).open(L('scar.png'))) > 127
    arr5 = np.where(scar5, arr5, 1e5)
    unk5 = zoom(unk.astype(np.float32), 2, order=1) * scar5
    sev5 = zoom(sev, 2, order=1)
    img = bpy.data.images.new('fx', width=Ww * 2, height=Hh * 2, alpha=True, float_buffer=True)
    img.colorspace_settings.name = 'Non-Color'
    FX['img'] = img
    build_terrain(step=2, with_canopy=False)
    add_pins()

    hot_ls = emissive('hot_ls', (1.0, 0.75, 0.2), 30)
    hot_v = emissive('hot_v', (0.3, 0.6, 1.0), 30)
    sph = bpy.data.meshes.new('s'); bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=6, radius=14); bm.to_mesh(sph); bm.free()
    marks = []
    for hs in P['hotspots']:
        t_obs = {'LANDSAT_NRT': 12 * 60 + 17, 'VIIRS_NOAA20_NRT': 14 * 60 + 49}.get(hs['source'])
        if t_obs is None or '2026-10-17' not in (hs['time_mdt'] or ''):
            continue
        me = sph.copy(); me.materials.append(hot_ls if t_obs < 13 * 60 else hot_v)
        ob = bpy.data.objects.new('mark', me); scn.collection.objects.link(ob)
        ob.location = (hs['x'], hs['y'], ground_z(hs['x'], hs['y']) + 20)
        marks.append((ob, t_obs))

    cam = camera(lens=30)
    c = P['scar_centroid']; tgt0 = Vector((c['x'], c['y'], ground_z(c['x'], c['y'])))
    N_FR = int(STORY[-1][0] * a.fps)

    def main_pose(u):
        ang = math.radians(212 + 14 * u); R, Hc = 5600 - 600 * u, 2700 - 300 * u
        return (tgt0 + Vector((R * math.sin(ang), R * math.cos(ang), Hc)), tgt0 + Vector((0, 0, -450)))

    def prologue_pose(k, nk):
        r11, ic = P['extra']['Range 11'], P['extra']['agl_impact_centre']
        # look past the firing line toward the impact zone so both sit in frame
        mx, my = r11['x'] + 0.78 * (ic['x'] - r11['x']), r11['y'] + 0.78 * (ic['y'] - r11['y'])
        ta = Vector((mx, my, ground_z(mx, my)))
        q = k / max(nk - 1, 1)
        ang = math.radians(248); R = 3600 - 250 * min(q / 0.55, 1); Hc = 2500
        loc_a, look_a = ta + Vector((R * math.sin(ang), R * math.cos(ang), Hc)), ta + Vector((0, 0, -550))
        if q <= 0.55:
            return loc_a, look_a
        s_ = (q - 0.55) / 0.45; s_ = s_ * s_ * (3 - 2 * s_)
        loc_b, look_b = main_pose(0)
        return loc_a.lerp(loc_b, s_), look_a.lerp(look_b, s_)

    if a.prologue:
        img.pixels.foreach_set(np.zeros(Hh * 2 * Ww * 2 * 4, np.float32) + np.tile([0, 0, 0, 1], Hh * 2 * Ww * 2).astype(np.float32))
        img.update()
        for ob, _ in marks:
            ob.hide_render = True
        pm = {}
        for k in range(a.start, a.end if a.end is not None else a.prologue):
            loc, look = prologue_pose(k, a.prologue)
            cam.location = loc; look_at(cam, look)
            scn.render.filepath = os.path.join(a.out, f'pro_{k:04d}.png')
            bpy.ops.render.render(write_still=True)
            pm[k] = {'screen': screen_points(cam), 'loc': list(loc), 'look': list(look)}
            json.dump(pm, open(os.path.join(a.out, f'pro_meta_{a.start:04d}.json'), 'w'))
            print('prologue', k, flush=True)
        sys.exit(0)
    end = a.end if a.end is not None else N_FR
    for f in range(a.start, end):
        sec = f / a.fps
        t = a.simtime if a.simtime is not None else sim_time(sec)
        u = f / max(N_FR - 1, 1)
        ang = math.radians(212 + 14 * u)
        R, Hc = 5600 - 600 * u, 2700 - 300 * u
        loc, look = main_pose(u)
        cam.location = loc; look_at(cam, look)
        # fire state at time t
        dt = t - arr5
        burning = dt >= 0
        tau = np.where(arr5 < FM['T_SHIFT'], 8.0, 1.2)   # minutes a cell keeps glowing (narrow front in the run)
        glow = np.where(burning, np.exp(-np.clip(dt, 0, None) / tau), 0.0) ** 2
        
        char = np.where(burning, np.clip(dt / 2.0, 0, 1), 0.0) * (0.6 + 0.4 * sev5)
        fade = np.clip((sec - FINAL_FADE[0]) / (FINAL_FADE[1] - FINAL_FADE[0]), 0, 1)
        rgba = np.zeros((Hh * 2, Ww * 2, 4), np.float32)
        rgba[..., 0] = char; rgba[..., 1] = np.clip(glow, 0, 1); rgba[..., 2] = unk5 * 0.8 * fade
        rgba[..., 3] = 1
        img.pixels.foreach_set(np.flipud(rgba).ravel())
        img.update()
        for ob, t_obs in marks:
            # a detection marker shows from its satellite pass until the wind shift
            ob.hide_render = not (t_obs <= t < FM['T_SHIFT'])
        scn.render.filepath = os.path.join(a.out, f'fire_{f:04d}.png' if a.simtime is None else f'still_{int(a.simtime)}_{f:04d}.png')
        bpy.ops.render.render(write_still=True)
        meta['frames'][f] = {'sec': sec, 't': t, 'screen': screen_points(cam),
                             'final_fade': float(fade)}
        if a.simtime is None:
            json.dump(meta, open(os.path.join(a.out, f'fire_meta_{a.start:04d}.json'), 'w'))
        print('frame', f, f'{int(t//60)}:{int(t%60):02d}', flush=True)
