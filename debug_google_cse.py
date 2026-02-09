"""
Debug script for Google Custom Search API (CSE) 403 error.
Tests API key, Search Engine ID, and API enablement.
"""

import os
import sys
try:
    import httpx
except ImportError:
    print("[FATAL] 'httpx' library is missing. Please run: pip install httpx")
    sys.exit(1)
import json
from pathlib import Path

# Fix Windows encoding issue
if sys.stdout.encoding and 'utf' not in sys.stdout.encoding.lower():
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("[WARN] 'python-dotenv' not installed. .env file might not be loaded.")
except Exception as e:
    print(f"[WARN] Error loading .env: {e}")

GOOGLE_CSE_API_KEY = os.getenv("GOOGLE_CSE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

print("=" * 70)
print("GOOGLE CUSTOM SEARCH (CSE) - 403 ERROR DEBUGGING")
print("=" * 70)

# Check 1: Environment variables
print("\n[1] Checking Environment Variables...")
if GOOGLE_CSE_API_KEY:
    print(f"  [OK] GOOGLE_CSE_API_KEY is set (length: {len(GOOGLE_CSE_API_KEY)})")
    # Show masked version for security
    masked = GOOGLE_CSE_API_KEY[:10] + "..." + GOOGLE_CSE_API_KEY[-5:]
    print(f"    Masked: {masked}")
else:
    print("  [ERROR] GOOGLE_CSE_API_KEY is NOT set in .env")
    print("    Fix: Add GOOGLE_CSE_API_KEY=your_api_key to .env")

if GOOGLE_CSE_ID:
    print(f"  [OK] GOOGLE_CSE_ID is set: {GOOGLE_CSE_ID}")
else:
    print("  [ERROR] GOOGLE_CSE_ID is NOT set in .env")
    print("    Fix: Add GOOGLE_CSE_ID=your_engine_id to .env")

if not (GOOGLE_CSE_API_KEY and GOOGLE_CSE_ID):
    print("\n[FATAL] Cannot proceed without both credentials.")
    print("\nTo get credentials:")
    print("  1. Go to https://programmablesearchengine.google.com/")
    print("  2. Click 'Create' and set up search engine for 'delhimetrorail.com'")
    print("  3. Copy the Engine ID (cx parameter)")
    print("  4. Go to https://console.cloud.google.com/")
    print("  5. Enable 'Custom Search API'")
    print("  6. Create an API Key under Credentials")
    print("  7. Add both to .env file")
    sys.exit(1)

# Check 2: Basic API connectivity
print("\n[2] Testing API Connectivity...")
try:
    with httpx.Client(timeout=10) as client:
        response = client.get("https://www.googleapis.com/customsearch/v1", 
                             params={"key": GOOGLE_CSE_API_KEY})
        print(f"  Connection: OK (HTTP {response.status_code})")
except Exception as e:
    print(f"  [ERROR] Connection failed: {e}")

# Check 3: Test with invalid search to see error details
print("\n[3] Testing Search with Minimal Query...")
test_query = "test DMRC metro"
params = {
    "key": GOOGLE_CSE_API_KEY,
    "cx": GOOGLE_CSE_ID,
    "q": test_query,
    "num": "1"
}

try:
    r = httpx.get("https://www.googleapis.com/customsearch/v1", params=params, timeout=10)
    print(f"  HTTP Status: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        items = data.get("items", [])
        print(f"  [SUCCESS] Got {len(items)} result(s)")
        if items:
            print(f"    - {items[0].get('title')}")
            print(f"      {items[0].get('link')}")
    else:
        print(f"  [ERROR] {r.status_code}")
        try:
            error_data = r.json()
            error = error_data.get("error", {})
            print(f"    Message: {error.get('message', 'N/A')}")
            print(f"    Code: {error.get('code', 'N/A')}")
            
            # Analysis of specific error codes
            code = error.get("code")
            if code == 403:
                print("\n  [ANALYSIS] 403 Error - Possible causes:")
                print("    - Custom Search API not enabled in Google Cloud")
                print("    - Search Engine (cx) ID is invalid")
                print("    - API key has wrong permissions")
                print("    - API key has quota limits exceeded")
            elif code == 400:
                print("\n  [ANALYSIS] 400 Error - Bad Request:")
                print("    - Invalid search query format")
                print("    - Missing required parameters")
            elif code == 429:
                print("\n  [ANALYSIS] 429 Error - Rate Limited:")
                print("    - Too many API requests")
                print("    - Wait before retrying")
            
            if "error_details" in error_data.get("error", {}):
                print(f"    Details: {error_data['error']['error_details']}")
                
        except:
            print(f"    Response: {r.text[:200]}")
except Exception as e:
    print(f"  [ERROR] Request failed: {e}")

# Check 4: Test DMRC-specific search
print("\n[4] Testing DMRC-Specific Search...")
dmrc_query = "strike status site:delhimetrorail.com"
params_dmrc = {
    "key": GOOGLE_CSE_API_KEY,
    "cx": GOOGLE_CSE_ID,
    "q": dmrc_query,
    "num": "3"
}

try:
    r = httpx.get("https://www.googleapis.com/customsearch/v1", params=params_dmrc, timeout=10)
    if r.status_code == 200:
        data = r.json()
        items = data.get("items", [])
        print(f"  [OK] Got {len(items)} DMRC result(s)")
        for i, item in enumerate(items[:2], 1):
            print(f"    {i}. {item.get('title')[:60]}...")
    else:
        print(f"  [ERROR] Failed: {r.status_code}")
        try:
            print(f"    Error: {r.json().get('error', {}).get('message', r.text[:100])}")
        except:
            print(f"    Response: {r.text[:100]}")
except Exception as e:
    print(f"  [ERROR] Request failed: {e}")

# Check 5: Recommendations based on 403
print("\n" + "=" * 70)
print("RECOMMENDATIONS")
print("=" * 70)

print("""
If you're getting 403 Forbidden:

STEP 1: Verify Search Engine Setup
  → Go to: https://programmablesearchengine.google.com/
  → Click 'My search engines'
  → Check if you have an active search engine
  → If not, create one:
      - Name: "DMRC Search"
      - Sites to search: Add "delhimetrorail.com" explicitly
      - Click Create
  → Copy the Engine ID (shown as "cx=...")
  → Update GOOGLE_CSE_ID in .env

STEP 2: Verify Custom Search API is Enabled
  → Go to: https://console.cloud.google.com/
  → Use top search to find "Custom Search API"
  → Click it and enable if not already enabled
  → Wait 10-15 seconds for this to take effect

STEP 3: Create/Verify API Key
  → In Google Cloud Console, go to "Credentials"
  → Look for an "API Key" (not OAuth or service account)
  → If none exists:
      - Click "+ Create Credentials"
      - Choose "API Key"
      - Copy it
      - Add to GOOGLE_CSE_API_KEY in .env

STEP 4: Restrict API Key to Custom Search (optional but recommended)
  → In Credentials, click on your API Key
  → Under "API restrictions", select "Custom Search API"
  → Save

STEP 5: Test Again
  → Update .env with new credentials
  → Restart the backend (Ctrl+C, then restart uvicorn)
  → Run this debug script again:
      python debug_google_cse.py
  → Or test via API:
      curl -X POST http://localhost:8000/assistant \\
        -H "Content-Type: application/json" \\
        -d '{
          "query":"Is there a strike today?",
          "language":"en"
        }'

STEP 6: If Still Failing
  → Check if you have a billing account in Google Cloud
  → 403 can also mean quota exceeded (edit .env and set):
      ASSISTANT_SIMULATE_LIVE=true
  → Or simply run the auto-fix script:
      python fix_and_run.py
  → This will use simulated results instead

""")

print("=" * 70)
print("For more help, see README.md - Troubleshooting section")
print("=" * 70)
