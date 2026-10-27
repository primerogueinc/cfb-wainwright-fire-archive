# GOES-18 / GOES-19 visible imagery, CFB Wainwright fire, Oct. 17, 2026, 14:30-17:30 MDT

Source: NOAA GOES-18 and GOES-19 ABI L1b Full Disk radiances (ABI-L1b-RadF, Mode 6, every 10 min), bands
C01 0.47 µm, C02 0.64 µm, C03 0.86 µm and C07 3.9 µm, from the public buckets `noaa-goes18` and `noaa-goes19`
(NOAA Open Data on AWS), day 290. No CONUS or mesoscale sector covered the fire, so Full Disk is the only option.
Only the HDF5 chunks covering 52.0-53.4 N, 111.8-109.6 W were read (HTTP range reads). No full-disk file was
stored. Script: `scripts/rubicon_ridge/goes_visible.py` (`extract`, then `render`).

## Bottom line

**Neither satellite shows an identifiable smoke plume from the fire between 14:30 and 17:30 MDT.**
We cannot give a plume direction or length from this imagery, and none should be claimed from it.

- **The fire is visible, but only as a hot spot.** The 3.9 µm signal at the fire centre shows the fire's
  run. A local anomaly >10 K appears on the GOES-19 15:20 scan (+19 K), GOES-18 15:30 (+28 K), both
  satellites at 15:40 (+28 to +33 K) and both at 15:50 (+11 to +13 K). Nothing remains by the 16:00 scan.
  This agrees with the earlier GOES-18 FDC detections (15:10 76 MW, 15:30 1,215 MW, 15:40 336 MW). The intense
  phase therefore spans roughly the 15:30 and 15:40 scans, about 20-30 minutes.
- **Cloud.** A NE-SW cold-frontal cloud band moves SE across the fire between about 15:10 and 15:40.
  The fire runs at its trailing edge, with broken frontal cumulus just N and W of the fire point. From about
  15:50 onward a dense field of post-frontal cumulus and stratocumulus covers the fire and everything downwind,
  through 17:30. Through the whole period, the SE half of the frame (the expected downwind sector) lies under
  a diffuse grey layer, probably thin pre-frontal mid/high cloud seen at a grazing angle. It is already
  there at 14:30, before the fire.
- **The clearest look is GOES-18 at 15:40 and 15:50.** In those scans a lane of mostly clear, dark ground
  runs SE from the fire for about 30-40 km before reaching the grey layer. No smoke streak is visible in that
  lane at this resolution. Faint grey texture there cannot be told apart from thin cloud or haze.
  Any smoke carried SE in the strong post-frontal wind would have run straight into the grey layer and,
  minutes later, the cumulus field. A short-lived, low, wind-bent grass-fire plume (not a pyrocumulus) would
  also be hard to see at these pixel sizes.
- **No pyrocumulus is visible.** Bright cloud near the fire at 15:20-15:40 moves with the frontal band and
  does not stay anchored to the fire. It cannot be attributed to the fire.
- **Better satellite: GOES-18**, slightly. It has the smaller view zenith (65.0° vs 68.8°), smaller pixels and
  a clearer view of the ground SE of the fire at 15:30-15:50. GOES-19 sees more of the frontal cloud over the
  fire (its 10.3 µm drops to 253 K at 15:30, from the earlier pull) and has more cloud-shadow and haze
  confusion. GOES-19's viewing geometry favours forward scattering, which brightens smoke, but that did not
  reveal a plume. GOES-19 has no FDC fire detection, although its 3.9 µm anomaly is clear at 15:20 and 15:40.
- **Side note (not a visible-band finding).** On the GOES-19 15:20 scan, the 3.9 µm burn-box maximum is
  304.6 K against a 284.6 K background. GOES-18's 15:20 scan was cloud-flagged at the fire. This warm signal
  comes before the ~15:29 front arrival, but it is a single 2 km pixel cluster at a 69° view angle and was
  not confirmed by FDC. Treat it as a lead to check, not a fact.

## Limits

- **Pixel size at the fire** (from adjacent pixel centres, `view_geometry.txt`). C02 is about 0.66 km E-W
  × 1.24 km N-S on GOES-18 and 0.80 × 1.41 km on GOES-19. C01/C03 are twice that (about 1.3-1.6 × 2.5-2.8 km)
  and C07 four times. The true-colour colour information is therefore about 1.5 × 2.7 km. Detail finer than
  about 2 km is not real.
- **Parallax.** Anything above the ground is drawn displaced away from the satellite: by 2.14 km per km of
  height toward azimuth 32° (NE) on GOES-18, and 2.57 km per km toward 318° (NW) on GOES-19. A plume or cloud
  top at 3 km would appear about 6.4 km NE (GOES-18) or 7.7 km NW (GOES-19) of its true position. The two
  satellites disagree on cloud positions by up to about 10 km for this reason. Terrain (about 0.7 km ASL)
  adds about 1.5-1.8 km of shift, which is not corrected.
- **Times.** Frames are labelled with the approximate time the fire latitude was imaged: scan start plus
  about 40 s (rows are swept north to south over about 9.3 min). This is accurate to about ±1 min. File
  names use the UTC scan start minute.
- **Processing.** Reflectance is computed as radiance × kappa0, with no solar-zenith or Rayleigh correction.
  The sun is low: solar zenith goes from 64° at 14:30 to 83° at 17:30. Each frame is contrast-enhanced on
  its own: a per-band dark offset is subtracted (only partly between bands), then a common gain and gamma
  0.75 are applied. Brightness therefore cannot be compared between frames, and the colours are an
  approximation. Green is synthesised as 0.45·C02 + 0.1·C03 + 0.45·C01.
  Frames are resampled to a 0.5 km azimuthal-equidistant grid centred on the fire (bilinear for
  reflectance, nearest-neighbour for C07).
- **Hot-pixel outline (red).** This marks C07 brightness temperature more than 10 K above the local 7×7
  median on the 2 km grid, restricted to within 15 km of the fire. It is a display aid, not a fire detection
  product. The outline is the shape of 2 km pixels projected at a steep angle.
- **Fire centre.** The marked point is 52.7645 N, 110.9052 W. Wainwright town is at 52.8334 N, 110.8601 W.

## Files

| File | What |
|---|---|
| `G18_visible_1430-1730MDT.gif` / `.mp4` | GOES-18 true-colour animation, 19 frames, 10-min steps |
| `G19_visible_1430-1730MDT.gif` / `.mp4` | GOES-19 true-colour animation |
| `frames_G18/`, `frames_G19/` | Per-scan PNGs: `G1x_truecolour_<UTC>.png` and `G1x_red_<UTC>.png` (C02 0.64 µm, finest resolution), 144 × 148 km, with fire point, Wainwright, 10 km bar, hot-pixel outline |
| `keyframes_1510-1600MDT_closeup.png` | 60 × 60 km close-ups, both satellites, 15:10-16:00 MDT, the key evidence figure |
| `crops_G18.nc`, `crops_G19.nc` | Cropped data: C01/C02/C03 reflectance factor, C07 brightness temperature, C02-grid lat/lon, fixed-grid x/y, projection attributes, per-scan end times |
| `view_geometry.txt` | View zenith, satellite azimuth, pixel spacing, parallax per km of height |

Credit: NOAA GOES-18/19 via NOAA Open Data on AWS.
