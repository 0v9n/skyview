# Skyview

Sky obstruction analyzer. Place a point anywhere on Earth and see how much of the sky is blocked by buildings and terrain using Google Photorealistic 3D Tiles.

## How it works

```
 skyview-standalone.html (single file, zero dependencies to install)
 ┌─────────────────────────────────────────────────────────────┐
 │                                                             │
 │   ┌──────────────┐    ┌──────────────┐   ┌──────────────┐   │
 │   │  CesiumJS    │    │  Raytrace    │   │  2D Polar    │   │
 │   │  3D Viewer   │───>│  Engine      │──>│  Plot        │   │
 │   └──────┬───────┘    └──────────────┘   └──────────────┘   │
 │          │                                                  │
 │          │ pickFromRay()                                    │
 │          v                                                  │
 │   ┌──────────────┐                                          │
 │   │  Google 3D   │                                          │
 │   │  Tiles API   │                                          │
 │   └──────────────┘                                          │
 │                                                             │
 └─────────────────────────────────────────────────────────────┘
```

### Raytrace pipeline

```
  Pin button → tap to place point
          │
          v
  ┌───────────────┐     Cast rays into hemisphere
  │  Point pos    │────> above the point
  │  (lat/lon/h)  │     (azimuth x elevation grid)
  └───────────────┘     Desktop: 72x15  Mobile: 36x10
          │
          v
  ┌───────────────┐     Each ray checked against
  │  pickFromRay  │────> Google Photorealistic 3D
  │  per ray      │     Tiles via Cesium scene
  └───────────────┘
          │
          v
  ┌───────────────┐     ┌───────────────┐
  │  Hit/miss     │────>│  Dome overlay │  3D: red/green cells
  │  results      │     │  on map       │  over the 3D view
  └───────────────┘     └───────────────┘
          │
          v
  ┌───────────────┐
  │  Polar plot   │  2D top-down obstruction map
  │  (top-right)  │  with obstruction % center
  └───────────────┘
```

### Beam geometry

```
          Zenith
            │
            │ ╱  beam cone
            │╱   (half-angle 55°)
            ┼─── pitch 15° from vertical
           ╱│
          ╱ │
   ──────╱──┼──── min elevation 35°
        ╱   │
  ─────╱────┴──── horizon
       point
```

## UI layout

Same layout on mobile and desktop:

```
 ┌──────────────────────────────┐
 │                    ┌───────┐ │
 │   3D Map           │ Polar │ │
 │                    │ Plot  │ │
 │         ·          │ 12.5% │ │
 │      (point)       │       │ │
 │                    └───────┘ │
 │                   lat, lon   │
 │                              │
 ├──────────────────────────────┤
 │  [ Search...        ] [pin]  │
 │  [ − Az + °  |  − ΔH + m  ]  │
 └──────────────────────────────┘
```

- **Polar plot** (top-right): always visible after placing a point, drag to aim azimuth
- **Clear sky %**: shown inside the polar plot center
  - Green: >= 85% clear
  - Yellow: >= 78% and < 85%
  - Red: < 78%
- **Lat/lon**: shown below the polar plot
- **Bottom bar** (row 1): search input + pin placement button
- **Bottom bar** (row 2): azimuth +/- (10° steps) + height +/- (1m steps)
- **Pin button**: tap to enter placement mode, tap map to place point. Pulses orange during raytrace
- **Dome overlay**: hides during camera movement (only cyan dot visible), reappears when idle

## Usage

**Hosted** — open [0v9n.github.io/skyview/skyview-standalone.html](https://0v9n.github.io/skyview/skyview-standalone.html)

**Local** — a local-development API key is bundled for running this repo on localhost. If needed, you can still use your own [Google Maps API key](https://developers.google.com/maps/documentation/tile/get-api-key) by replacing it in the HTML:

```js
const sceneConfig = { api_key: 'YOUR_API_KEY_HERE', ... };
```

Then run `python3 serve.py` (opens browser automatically on `:8090`)

### Desktop + mobile validation

To verify zoom-flow parity in both profiles with the built-in benchmark hook:

1. Start a local server:

```bash
python3 -m http.server 8090 --bind 0.0.0.0
```

2. Run the benchmark script (requires Python Playwright):

```bash
python3 scripts_zoom_benchmark.py --url http://localhost:8090/skyview-standalone.html --trials 5
```

This prints desktop/mobile medians and `%` step overhead for mobile vs desktop.

### Implementation notes (UX presets)

Built-in scene presets used for screenshots and quick reset:

1. **Tower single** (anchor)
2. **Tower dual** (side offsets)
3. **Random single** (predefined lat/lon + dH/yaw)
4. **Random dual** (predefined lat/lon + offsets + `yawB = yawA + 180`)

On first load, preset **1 (Tower single)** is auto-applied and camera framing is tuned to a neighborhood-level view with a slight vertical offset so the tower remains clear above the bottom bar.

If Python Playwright is unavailable, the script prints a JSON `status: "skipped"` payload with manual console commands so you can still test desktop/mobile quickly from browser DevTools.

### Controls

| Input | Action |
|---|---|
| Pin button | Enter placement mode, tap map to place |
| Right-click (desktop) | Place point directly |
| Drag | Orbit camera |
| Scroll / Pinch | Zoom (altitude-proportional) |
| R (desktop) | Reset camera |
| Search bar | Fly to location (name or `lat, lon`) |
| Drag polar plot | Aim beam azimuth direction |
| Az +/- | Rotate beam 10° increments |
| ΔH +/- | Raise/lower point 1m increments |

### Performance

- Desktop: 72x15 = 1080 rays, ~1-2s raytrace
- Mobile: 36x10 = 360 rays, ~1s raytrace
- Dome overlay hides during camera movement for smooth orbiting
- Cyan point marker stays visible during movement
- Camera inertia tuned to match Google Earth feel
- Pin button pulses orange during raytrace processing

## Known issues

### Desktop (Chrome, Firefox, Safari)

- **Point placement accuracy**: clicking on a rooftop or tower top at an oblique angle sometimes places the point behind the intended surface rather than on it. The `pickPosition` depth buffer may not match the visual at steep angles. Right-click placement is affected the same way as pin-button placement.
- **Zoom feel**: scroll wheel zoom does not feel as smooth or proportional as Google Earth. Currently using Cesium defaults. Needs tuning to match the Google Earth scroll-to-zoom curve where each tick moves a consistent percentage of current altitude.
- **Raytrace can still cause brief UI stalls**: despite chunked async processing, each chunk (12 azimuth rows) runs synchronously and can block the thread for ~100-200ms. Fast interactions during raytrace may feel sluggish.

### Mobile (iOS Safari, Android Chrome)

- **Point placement accuracy**: same depth-buffer issue as desktop, but more noticeable because tap positions are less precise than mouse clicks. The placed point often appears offset from where the user tapped, especially on angled surfaces.
- **Page occasionally stops responding**: the tool intermittently freezes and then recovers after a few seconds. Likely related to 3D tile loading pressure, garbage collection, or the raytrace competing with Cesium's render loop. Tab may be killed by the OS under memory pressure.
- **Zoom and orbit feel**: pinch-to-zoom and drag-to-orbit do not match the smoothness of Google Earth. Cesium's mobile touch handling has more friction and less momentum than expected.
- **Pin button processing indicator**: the orange pulse on the pin button during raytrace is not always visible, especially if the raytrace completes quickly or if the button is partially occluded by the keyboard.
- **3D tile loading**: tiles can load slowly on mobile (10 concurrent requests). If a point is placed before high-detail tiles finish loading, the raytrace runs against coarse geometry and produces inaccurate obstruction results.

### Both platforms

- **No feedback on pick failure**: if you tap an area where tiles have not loaded yet, the pick silently fails (pin flashes red briefly but is easy to miss). Needs a clearer indication that the user should wait for tiles to load.
- **Dome overlay disappears during camera movement**: the 3D dome overlay hides while orbiting and only the cyan dot remains. When the camera stops, the overlay redraws. This can feel jarring when making small adjustments — the dome flickers off and on.
- **Raytrace not triggered on camera stop**: if the camera moves after placing a point (changing the view angle), the dome overlay reprojects but does NOT re-raytrace. The obstruction data may be stale if the point is near the edge of loaded tiles.

## Files

```
skyview/
├── skyview-standalone.html   Single-file app (HTML + CSS + JS)
└── serve.py                  Local dev server (Python 3)
```
