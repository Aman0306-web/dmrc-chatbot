#!/usr/bin/env python
"""Test all API routes to verify they are working."""

import urllib.request
import json
import sys

endpoints = [
    ('GET', 'http://127.0.0.1:8000/', 'Root'),
    ('GET', 'http://127.0.0.1:8000/lines', 'Lines (original)'),
    ('GET', 'http://127.0.0.1:8000/api/lines', 'Lines (enhanced)'),
    ('GET', 'http://127.0.0.1:8000/api/fuzzy-search?q=khan', 'Fuzzy Search'),
    ('GET', 'http://127.0.0.1:8000/api/autocomplete?q=raj', 'Autocomplete'),
    ('GET', 'http://127.0.0.1:8000/api/best-match?q=chandi%20chawk', 'Best Match'),
    ('GET', 'http://127.0.0.1:8000/station/Khan%20Market', 'Station Info'),
    ('GET', 'http://127.0.0.1:8000/emergency', 'Emergency'),
]

print("\n" + "="*70)
print("ROUTE VERIFICATION TEST")
print("="*70 + "\n")

passed = 0
failed = 0

for method, url, description in endpoints:
    try:
        req = urllib.request.urlopen(url)
        status = req.status
        data = json.loads(req.read())
        print(f"✅ [{status}] {description}")
        print(f"   → {method} {url.split('8000')[1][:50]}")
        passed += 1
    except urllib.error.HTTPError as e:
        print(f"❌ [HTTP {e.code}] {description}")
        print(f"   → {method} {url.split('8000')[1][:50]}")
        failed += 1
    except Exception as e:
        print(f"❌ [ERROR] {description}")
        print(f"   → {str(e)[:60]}")
        failed += 1

print("\n" + "="*70)
print(f"RESULTS: {passed} passed ✅  |  {failed} failed ❌")
print("="*70 + "\n")

sys.exit(0 if failed == 0 else 1)
