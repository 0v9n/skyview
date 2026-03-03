# Latest Validation Results

Executed against local server (`http://localhost:8090/skyview-standalone.html`) with both shell checks and browser automation.

## 1) Benchmark script fallback proof (no Python Playwright)

Command:

```bash
python3 scripts_zoom_benchmark.py --url http://localhost:8090/skyview-standalone.html --trials 1
```

Observed behavior:
- Prints clear dependency message: `Playwright Python package is not installed...`.
- Exits successfully with fallback JSON.
- Runs static UX checks with all required layout checks passing:
  - `has_bottom_bar: true`
  - `search_width_clamp: true`
  - `dh_group_fixed_width: true`
  - `icon_square_40: true`
  - `single_row_nowrap: true`

## 2) Browser automation UX evidence (desktop + mobile)

Automated browser run collected real layout/runtime metrics and screenshots.

### Desktop (1440×900)
- `wrap: nowrap`
- `controlHeights: [40, 40, 40, 40]`
- `barWidth: 464`
- `status: Clear sky 100.0%`
- `errors: []`

### Mobile (iPhone 13 profile)
- `viewportWidth: 390`
- `wrap: nowrap`
- `overflowsViewport: false`
- `searchWidth: 163.796875`
- `controlHeights: [40, 40, 40, 40]`
- `status: Coop`
- `errors: []`

## 3) Syntax check

Command:

```bash
python3 -m py_compile scripts_zoom_benchmark.py
```

Result: pass.
