# Skyview

Antenna obstruction analyzer. Place an antenna anywhere on Earth and instantly see what portion of the sky is clear vs blocked by buildings and terrain.

## How it works

```
 skyview-standalone.html (single file, zero dependencies to install)
 ┌─────────────────────────────────────────────────────────────┐
 │                                                             │
 │   ┌──────────────┐    ┌──────────────┐   ┌──────────────┐  │
 │   │  CesiumJS    │    │  Raytrace    │   │  UI Panel    │  │
 │   │  3D Viewer   │───>│  Engine      │──>│  + Polar Plot│  │
 │   └──────┬───────┘    └──────────────┘   └──────────────┘  │
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
  Right-click places antenna
          │
          v
  ┌───────────────┐     Cast 72 x 15 rays into
  │  Antenna pos  │────> hemisphere above antenna
  │  (lat/lon/h)  │     (azimuth x elevation grid)
  └───────────────┘
          │
          v
  ┌───────────────┐     Each ray checked against
  │  pickFromRay  │────> Google Photorealistic 3D
  │  per ray      │     Tiles via Cesium scene
  └───────────────┘
          │
          v
  ┌───────────────┐     ┌───────────────┐
  │  Hit/miss     │────>│  Dome overlay │  2D canvas over 3D view
  │  results      │     │  (red/green)  │  reprojected on camera move
  └───────────────┘     └───────────────┘
          │
          v
  ┌───────────────┐
  │  Polar plot   │  Top-down sky map with % clear
  └───────────────┘
```

### Beam geometry

```
          Zenith
            │
            │  ╱ beam cone
            │╱   (half-angle 55°)
            ┼─── pitch 15° from vertical
           ╱│
          ╱  │
   ──────╱───┼──── min elevation 35°
        ╱    │
  ─────╱─────┴───── horizon
       antenna
```

## Usage

**Hosted** — open [0v9n.github.io/skyview/skyview-standalone.html](https://0v9n.github.io/skyview/skyview-standalone.html)

**Local** — run `python3 serve.py` (opens browser automatically on `:8090`)

### Controls

| Input | Action |
|---|---|
| Right-click | Place antenna |
| Drag | Orbit camera |
| R | Reset camera |
| Search bar | Fly to location (name or `lat, lon`) |
| Azimuth slider | Rotate beam direction |
| Height slider | Raise antenna above surface |

## Files

```
skyview/
├── skyview-standalone.html   Single-file app (HTML + CSS + JS)
└── serve.py                  Local dev server (Python 3)
```
