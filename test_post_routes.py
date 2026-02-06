#!/usr/bin/env python
"""Test POST endpoints for chat, routing, and assistant."""

import urllib.request
import json
import sys

post_tests = [
    {
        'url': 'http://127.0.0.1:8000/chat',
        'data': {'message': 'What is the fastest route from Rajiv Chowk to Khan Market?', 'language': 'en'},
        'desc': 'Chat endpoint'
    },
    {
        'url': 'http://127.0.0.1:8000/route',
        'data': {'from_station': 'Rajiv Chowk', 'to_station': 'Khan Market', 'language': 'en'},
        'desc': 'Route finding'
    },
]

print("\n" + "="*70)
print("POST ENDPOINT TEST")
print("="*70 + "\n")

passed = 0
failed = 0

for test in post_tests:
    try:
        data = json.dumps(test['data']).encode('utf-8')
        req = urllib.request.Request(
            test['url'],
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        response = urllib.request.urlopen(req)
        status = response.status
        result = json.loads(response.read())
        print(f"✅ [{status}] {test['desc']}")
        print(f"   → POST {test['url'].split('8000')[1]}")
        passed += 1
    except urllib.error.HTTPError as e:
        print(f"❌ [HTTP {e.code}] {test['desc']}")
        try:
            error_msg = json.loads(e.read())
            print(f"   → Error: {error_msg.get('detail', str(e))[:60]}")
        except:
            print(f"   → Error: {str(e)[:60]}")
        failed += 1
    except Exception as e:
        print(f"❌ [ERROR] {test['desc']}")
        print(f"   → {str(e)[:60]}")
        failed += 1

print("\n" + "="*70)
print(f"POST RESULTS: {passed} passed ✅  |  {failed} failed ❌")
print("="*70 + "\n")

sys.exit(0 if failed == 0 else 1)
