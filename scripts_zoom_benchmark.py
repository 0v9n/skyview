#!/usr/bin/env python3
"""Run Skyview zoom parity benchmark for desktop and mobile profiles.

Usage:
  1) Start a local server in repo root:
       python3 -m http.server 8090 --bind 0.0.0.0
  2) Run this script:
       python3 scripts_zoom_benchmark.py --url http://localhost:8090/skyview-standalone.html --trials 5
"""

import argparse
import asyncio
import json
import statistics
import sys
from typing import Dict, List

try:
    from playwright.async_api import async_playwright
except ModuleNotFoundError:  # pragma: no cover - environment-dependent import path
    async_playwright = None


async def run_trial(browser, url: str, mobile: bool, start_height: int, target_height: int, max_steps: int, settle_ms: int):
    if mobile:
        context = await browser.new_context(
            viewport={"width": 390, "height": 844},
            user_agent=(
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
                "Mobile/15E148 Safari/604.1"
            ),
            has_touch=True,
            is_mobile=True,
            device_scale_factor=3,
        )
    else:
        context = await browser.new_context(viewport={"width": 1366, "height": 768})

    page = await context.new_page()
    await page.goto(url, wait_until="domcontentloaded", timeout=120000)
    await page.wait_for_timeout(2500)
    result = await page.evaluate(
        """async ({startHeight, targetHeight, maxSteps, settleMs}) => {
            if (!window.__skyviewDebug?.runSyntheticZoomBenchmark) {
              throw new Error('window.__skyviewDebug.runSyntheticZoomBenchmark is missing');
            }
            return await window.__skyviewDebug.runSyntheticZoomBenchmark({
              startHeight,
              targetHeight,
              maxSteps,
              settleMs,
            });
        }""",
        {
            "startHeight": start_height,
            "targetHeight": target_height,
            "maxSteps": max_steps,
            "settleMs": settle_ms,
        },
    )
    await context.close()
    return result


def summarize(rows: List[Dict]):
    steps = [r["steps"] for r in rows]
    elapsed = [r["elapsedMs"] for r in rows]
    return {
        "trials": len(rows),
        "median_steps": statistics.median(steps),
        "p95_steps": sorted(steps)[max(0, int(0.95 * len(steps)) - 1)],
        "median_elapsed_ms": statistics.median(elapsed),
        "median_end_height": statistics.median([r["endHeight"] for r in rows]),
    }


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8090/skyview-standalone.html")
    parser.add_argument("--trials", type=int, default=5)
    parser.add_argument("--start-height", type=int, default=2000)
    parser.add_argument("--target-height", type=int, default=200)
    parser.add_argument("--max-steps", type=int, default=120)
    parser.add_argument("--settle-ms", type=int, default=8)
    args = parser.parse_args()

    if async_playwright is None:
        print(
            json.dumps(
                {
                    "status": "skipped",
                    "reason": "python_playwright_missing",
                    "message": (
                        "Python package 'playwright' is not installed in this environment. "
                        "Install it and run again, or run manual benchmark commands in browser console."
                    ),
                    "manual_console_commands": {
                        "desktop": (
                            "await window.__skyviewDebug.runSyntheticZoomBenchmark({"
                            "startHeight:2000,targetHeight:200,maxSteps:120,settleMs:8})"
                        ),
                        "mobile": (
                            "Open DevTools device emulation first, then run: "
                            "await window.__skyviewDebug.runSyntheticZoomBenchmark({"
                            "startHeight:2000,targetHeight:200,maxSteps:120,settleMs:8})"
                        ),
                    },
                },
                indent=2,
            )
        )
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        desktop_rows, mobile_rows = [], []

        for _ in range(args.trials):
            desktop_rows.append(
                await run_trial(
                    browser,
                    args.url,
                    mobile=False,
                    start_height=args.start_height,
                    target_height=args.target_height,
                    max_steps=args.max_steps,
                    settle_ms=args.settle_ms,
                )
            )
            mobile_rows.append(
                await run_trial(
                    browser,
                    args.url,
                    mobile=True,
                    start_height=args.start_height,
                    target_height=args.target_height,
                    max_steps=args.max_steps,
                    settle_ms=args.settle_ms,
                )
            )

        await browser.close()

    report = {
        "desktop": {"summary": summarize(desktop_rows), "trials": desktop_rows},
        "mobile": {"summary": summarize(mobile_rows), "trials": mobile_rows},
    }
    report["step_overhead_pct_mobile_vs_desktop"] = round(
        (report["mobile"]["summary"]["median_steps"] / report["desktop"]["summary"]["median_steps"] - 1) * 100,
        2,
    )

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
