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
- **Obstruction %**: shown inside the polar plot center
  - Green: < 15%
  - Yellow: >= 15% and < 22%
  - Red: >= 22%
- **Lat/lon**: shown below the polar plot
- **Bottom bar**: single-row controls (search + dH stepper + pin + menu)
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

If Python Playwright is unavailable, the script runs static UX checks and exits non-zero on failure, while still printing manual console commands for browser-side benchmarking.

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
| dH - / + | Lower/raise selected observer height |
| ⋯ menu | Presets and observer actions |

### Performance

- Desktop: 72x15 = 1080 rays, ~1-2s raytrace
- Mobile: 36x10 = 360 rays, ~1s raytrace
- Dome overlay hides during camera movement for smooth orbiting
- Cyan point marker stays visible during movement
- Camera inertia tuned to match Google Earth feel
- Pin button pulses orange during raytrace processing

## Files

```
skyview/
├── skyview-standalone.html   Single-file app (HTML + CSS + JS)
├── scripts_zoom_benchmark.py Desktop/mobile parity + static UX checks
└── serve.py                  Local dev server (Python 3)
```
