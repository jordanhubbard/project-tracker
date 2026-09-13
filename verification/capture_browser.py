#!/usr/bin/env python3
"""Capture a locally running disposable tracker for manual visual review.

This checks rendering health; screenshots alone do not verify product behavior.
Usage: python verification/capture_browser.py http://127.0.0.1:8765
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright


def capture(base: str, output: Path, executable: str | None) -> None:
    parsed = urlparse(base)
    if parsed.scheme != 'http' or parsed.hostname not in ('127.0.0.1', 'localhost'):
        raise ValueError('Use a disposable localhost service for browser verification')
    output.mkdir(parents=True, exist_ok=True)
    results = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, executable_path=executable)
        try:
            for name, width, height in [('desktop', 1440, 1000), ('mobile', 390, 844)]:
                context = browser.new_context(viewport={'width': width, 'height': height})
                page = context.new_page()
                issues = []
                page.on('pageerror', lambda error: issues.append(str(error)))
                page.on('console', lambda message: issues.append(message.text)
                        if message.type == 'error' else None)
                page.on('requestfailed', lambda request: issues.append(
                    f'{request.method} {request.url}: {request.failure}'))
                page.on('response', lambda response: issues.append(
                    f'HTTP {response.status}: {response.url}') if response.status >= 400 else None)
                page.goto(base, wait_until='domcontentloaded')
                page.wait_for_timeout(1500)
                page.screenshot(path=str(output / f'{name}.png'), full_page=True)
                (output / f'{name}.aria.txt').write_text(page.locator('body').aria_snapshot())
                dimensions = page.evaluate('''() => ({
                    viewport: innerWidth, document: document.documentElement.scrollWidth
                })''')
                if dimensions['document'] > dimensions['viewport']:
                    issues.append(f'Document overflow: {dimensions}')
                body = page.locator('body').inner_text()
                for invalid in ('NaN', 'Infinity', '[object Object]'):
                    if invalid in body:
                        issues.append(f'Invalid rendered value: {invalid}')
                results.append({'viewport': name, 'issues': issues, 'dimensions': dimensions})
                context.close()
        finally:
            browser.close()
    (output / 'rendering.json').write_text(json.dumps(results, indent=2) + '\n')
    print(json.dumps(results, indent=2))
    if any(result['issues'] for result in results):
        raise SystemExit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('url')
    parser.add_argument('--output', type=Path, default=Path('_build/browser-review'))
    chrome = Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
    parser.add_argument('--browser', default=str(chrome) if chrome.exists() else None)
    arguments = parser.parse_args()
    capture(arguments.url, arguments.output, arguments.browser)
