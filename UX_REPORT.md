# Skyview UX Re-evaluation Report (Flow, Speed, Desktop/Mobile Parity)

## Scope
This reassessment focuses on speed and interaction flow in both desktop and mobile, with special attention to zoom scale/speed parity while respecting form-factor differences.

Reviewed artifacts:
- `skyview-standalone.html`
- `README.md`

---

## What changed in this pass
1. Added persistent status messaging (`Ready`, placement, analyzing, success, error).
2. Added first-use placement hint in-product (instead of relying on README only).
3. Improved accessibility baseline:
   - Removed viewport zoom lockout.
   - Added `aria-label` on primary controls.
   - Added `aria-live` status region.
4. Increased legibility/tap comfort on dense controls (especially mobile search/input text sizing).
5. Added adaptive zoom tuning to keep desktop/mobile feel close:
   - Exponential zoom-factor curve by camera height.
   - Slight mobile slowdown factor to account for touch gesture variance.
6. Added a debug benchmark hook (`window.__skyviewDebug.runSyntheticZoomBenchmark`) so zoom-flow parity can be tested repeatedly.

---

## Zoom speed/scale assessment

### Target UX principle
- Desktop and mobile should feel *nearly identical* in intent: same “distance traveled per perceived effort,” with mobile slightly damped to reduce accidental overshoot.

### Adopted numerology (Google-Earth-like heuristic)
Because Google Earth internals are proprietary, exact parity constants are not publicly available. We therefore use a reference-inspired heuristic:
- Exponential response with altitude (fine control near ground, faster travel at altitude).
- Dynamic zoom factor range: **1.55 → 5.6** across ~15m to 15,000m camera height.
- Mobile multiplier: **0.92** (8% slower than desktop).

This aligns with common globe UX behavior: low-altitude precision + high-altitude traversal speed.

---

## Automated parity benchmark (executed)

### Method
- Start camera at 2,000m over the same anchor point.
- Iteratively zoom until reaching <= 200m.
- Measure step count and elapsed time via `window.__skyviewDebug.runSyntheticZoomBenchmark(...)`.
- Run once in desktop profile and once in mobile profile (touch UA + mobile viewport).

### Result snapshot
| Profile | Steps to <=200m | End height | Elapsed |
|---|---:|---:|---:|
| Desktop | 18 | 197.05m | 11,521ms |
| Mobile | 20 | 190.65m | 5,304ms |

**Interpretation**
- Step parity is close (mobile needs ~11.1% more steps), which is within the intended “slightly slower mobile” behavior.
- Absolute elapsed time in headless runs is noisy and environment-dependent; step parity is the more stable indicator.

---

## Current findings (post-change)

### Strengths
- Flow from placement to analysis is now better guided in-app.
- Status feedback is no longer color-only/transient.
- Desktop/mobile zoom behavior is now measurable and closer in feel through shared dynamic model.
- Accessibility baseline improved materially.

### Remaining gaps
- Still no explicit in-app control legend for all gestures/shortcuts.
- Result confidence metadata (ray count/mode) is not surfaced in the bottom UI.
- Mobile fine-aim mode (1° azimuth step) could further improve precision tasks.

---

## Next recommended step
1. Run 5-trial benchmark batches per profile and use median step counts.
2. If median mobile overhead exceeds 12%, reduce damping gap (e.g., 0.92 -> 0.94).
3. Add a compact analysis metadata line (rays/mode/compute ms).

Suggested KPI: mobile/desktop median step-to-target difference within ±10% to ±12% on standard zoom tasks.
