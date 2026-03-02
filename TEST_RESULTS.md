# Latest Validation Results

Executed against local server (`http://localhost:8090/skyview-standalone.html`) using Playwright browser tooling.

## Zoom benchmark (synthetic)

Command evaluated in browser (both profiles):

```js
await window.__skyviewDebug.runSyntheticZoomBenchmark({
  startHeight: 2000,
  targetHeight: 200,
  maxSteps: 120,
  settleMs: 8,
})
```

### Desktop profile
- steps: **18**
- endHeight: **197.0548m**
- elapsedMs: **10194**
- zoomFactor(final): **3.7753**

### Mobile profile
- steps: **20**
- endHeight: **190.6491m**
- elapsedMs: **5354**
- zoomFactor(final): **3.4605**

### Parity summary
- Mobile step overhead vs desktop: **+11.1%** (`20 / 18 - 1`).
- This remains within the currently targeted “slightly slower on mobile” behavior envelope.

## Artifacts
- Desktop screenshot: `desktop-benchmark-latest.png`
- Mobile screenshot: `mobile-benchmark-latest.png`
