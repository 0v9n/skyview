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
- **Bottom bar** (row 1): search input + pin placement button
- **Bottom bar** (row 2): azimuth +/- (10° steps) + height +/- (1m steps)
- **Pin button**: tap to enter placement mode, tap map to place point. Pulses orange during raytrace
- **Dome overlay**: hides during camera movement (only cyan dot visible), reappears when idle

## Usage

**Hosted** — open [0v9n.github.io/skyview/skyview-standalone.html](https://0v9n.github.io/skyview/skyview-standalone.html)

**Local** — the bundled API key is restricted to the hosted URL above. To run locally, get your own [Google Maps API key](https://developers.google.com/maps/documentation/tile/get-api-key) and replace it in the HTML:

```js
const sceneConfig = { api_key: 'YOUR_API_KEY_HERE', ... };
```

Then run `python3 serve.py` (opens browser automatically on `:8090`)

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

## Files

```
skyview/
├── skyview-standalone.html   Single-file app (HTML + CSS + JS)
└── serve.py                  Local dev server (Python 3)
```
