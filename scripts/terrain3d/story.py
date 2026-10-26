"""Storyboard for the full-timeline 3D reconstruction (no Blender imports).

Every frame has a clock time and a camera. Camera shots that hold still are
rendered once and reused; the fire, night, flames, smoke, figures and text are
all composited per frame (compose_story.py), so changing the timeline costs
seconds, not hours.

Shots
  B  wide view of the whole burn from the south-southwest (the earlier camera)
  A  behind Range 11's firing line, looking east-northeast at the impact area
  C  close on Range 2 and the road head, from the southwest, for the escape scenarios
"""
import math, json, os
import numpy as np

FPS = 12


def hm(h, m=0):
    return h * 60 + m


def smooth(q):
    q = min(max(q, 0.0), 1.0)
    return q * q * (3 - 2 * q)


class Story:
    def __init__(self, layers):
        P = json.load(open(os.path.join(layers, 'points.json')))
        self.P = P
        self.h = np.load(os.path.join(layers, 'height.npy')).astype(np.float64)
        self.Z0 = float(np.percentile(self.h, 1))
        self.RES = P['grid']['res']
        c = P['scar_centroid']; self.tgt0 = np.array([c['x'], c['y'], self.gz(c['x'], c['y'])])
        self.poses = {'A': self.pose_A(), 'B': self.pose_B(), 'C': self.pose_C()}
        # (seconds, clock minutes, shot or (shotFrom, shotTo)) keyframes; clock is piecewise linear
        S = []
        def seg(dur, t0, t1, shot, **kw):
            S.append(dict(dur=dur, t0=t0, t1=t1, shot=shot, **kw))
        seg(3.0, hm(4, 30), hm(4, 50), 'B', card='forecast')
        seg(2.0, hm(4, 50), hm(5, 20), ('B', 'A'))
        seg(6.0, hm(5, 20), hm(11, 40), 'A')
        seg(2.0, hm(11, 40), hm(12, 17), ('A', 'B'))
        seg(1.5, hm(12, 17), hm(12, 17), 'B')
        seg(2.5, hm(12, 17), hm(14, 14), 'B')
        seg(1.5, hm(14, 14), hm(14, 18), 'B', card='warning')
        seg(1.2, hm(14, 18), hm(14, 49), 'B')
        seg(1.0, hm(14, 49), hm(14, 50), 'B')
        seg(1.5, hm(14, 50), hm(15, 16), 'B')
        seg(1.2, hm(15, 16), hm(15, 16.2), 'B', card='gust')
        seg(1.5, hm(15, 16.2), hm(15, 16.8), ('B', 'C'))
        seg(10.0, hm(15, 16.8), hm(15, 31), 'C')
        seg(1.5, hm(15, 31), hm(15, 40), ('C', 'B'))
        seg(1.5, hm(15, 40), hm(15, 45), 'B')
        seg(2.5, hm(15, 45), hm(15, 45), 'B', final=True)
        self.segs = S
        self.frames = []
        for si, s in enumerate(S):
            n = int(round(s['dur'] * FPS))
            for k in range(n):
                q = k / n
                t = s['t0'] + (s['t1'] - s['t0']) * q
                if isinstance(s['shot'], tuple):
                    a, b = s['shot']; w = smooth(q)
                    key = f"{a}{b}_{si}_{k:03d}"
                    la, lk = self.poses[a]; lb, lkb = self.poses[b]
                    loc = la + (lb - la) * w; look = lk + (lkb - lk) * w
                else:
                    key = s['shot']; loc, look = self.poses[key]
                self.frames.append(dict(i=len(self.frames), seg=si, q=q, t=t, key=key,
                                        loc=loc.tolist(), look=look.tolist(),
                                        card=s.get('card'), final=s.get('final', False)))

    def gz(self, x, y):
        h = self.h; RES = self.RES
        fc = np.clip(x / RES, 0, h.shape[1] - 2); fr = np.clip(h.shape[0] - 1 - y / RES, 0, h.shape[0] - 2)
        c, r = int(fc), int(fr); dc, dr = fc - c, fr - r
        b = h[r:r + 2, c:c + 2]
        v = b[0, 0] * (1 - dc) * (1 - dr) + b[0, 1] * dc * (1 - dr) + b[1, 0] * (1 - dc) * dr + b[1, 1] * dc * dr
        return (v - self.Z0) * 3.0

    def pose_B(self):
        ang = math.radians(212); R, Hc = 5600, 2700
        return (self.tgt0 + np.array([R * math.sin(ang), R * math.cos(ang), Hc]), self.tgt0 + np.array([0, 0, -450]))

    def pose_A(self):
        r11, ic = self.P['extra']['Range 11'], self.P['extra']['agl_impact_centre']
        mx, my = r11['x'] + 0.78 * (ic['x'] - r11['x']), r11['y'] + 0.78 * (ic['y'] - r11['y'])
        ta = np.array([mx, my, self.gz(mx, my)])
        ang = math.radians(248); R, Hc = 3350, 2500
        return (ta + np.array([R * math.sin(ang), R * math.cos(ang), Hc]), ta + np.array([0, 0, -550]))

    def pose_C(self):
        a, b = self.P['pov']['Range 2'], self.P['pov']['Roadhead']
        # frame Range 2, the road head and the escape route east-northeast (to ~600 m out)
        mx = (a['x'] + b['x']) / 2 + 250; my = (a['y'] + b['y']) / 2 + 60
        ta = np.array([mx, my, self.gz(mx, my)])
        ang = math.radians(215); R, Hc = 2300, 1250
        return (ta + np.array([R * math.sin(ang), R * math.cos(ang), Hc]), ta + np.array([0, 0, -150]))

    def unique_renders(self):
        seen = {}
        for f in self.frames:
            seen.setdefault(f['key'], (f['loc'], f['look']))
        return seen


if __name__ == '__main__':
    import sys
    s = Story(sys.argv[1])
    print(len(s.frames), 'frames,', f"{len(s.frames) / FPS:.1f} s;", len(s.unique_renders()), 'renders')
    json.dump({'frames': s.frames}, open(os.path.join(sys.argv[1], 'story.json'), 'w'))
