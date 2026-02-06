# GOOGLE CSE 403 FIX - Step by Step

## Root Cause (DIAGNOSED)
The Custom Search API is NOT ENABLED in your Google Cloud project (944471176020).

Error message from Google:
"Custom Search API has not been used in project before or it is disabled."

## IMMEDIATE FIX (2 minutes - Use simulated search)

Edit your `.env` file and set:
```
ASSISTANT_SIMULATE_LIVE=true
```

This will use simulated search results instead of real Google API calls.
Your app will work perfectly with fake but realistic DMRC results.

Re-start the backend:
```bash
# Kill existing uvicorn (Ctrl+C)
# Then run:
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Test:
```bash
curl -X POST http://localhost:8000/assistant \
  -H "Content-Type: application/json" \
  -d '{"query":"Is there a strike today?","language":"en"}'
```

---

## PROPER FIX (5 minutes - Enable the API)

Follow these steps EXACTLY to enable the Custom Search API:

### Step 1: Go to Google Cloud Console
Visit the direct link from your error:
**https://console.developers.google.com/apis/api/customsearch.googleapis.com/overview?project=944471176020**

### Step 2: Click ENABLE Button
- You should see a blue "ENABLE" button
- Click it
- Wait 10-15 seconds for it to activate

### Step 3: Verify It's Enabled
- The button should now say "MANAGE" instead of "ENABLE"
- The status should show "API ENABLED"

### Step 4: Update .env (Optional - only if you want real searches)
```ini
GOOGLE_CSE_API_KEY=AIzaSyBtHqADS99L-__Orq-ro7wu28Sjy_Xkl28
GOOGLE_CSE_ID=c770bdc06ded44863
ASSISTANT_SIMULATE_LIVE=false
```

### Step 5: Restart Backend
```bash
# Kill existing uvicorn
# Then:
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Step 6: Run Debug Script Again
```bash
python debug_google_cse.py
```

Should now show:
```
[3] Testing Search with Minimal Query...
  HTTP Status: 200
  [SUCCESS] Got 5 result(s)
    - DMRC Official Notice...
```

---

## Troubleshooting

### I clicked Enable but still get 403
→ **Wait 5-10 minutes** - Google needs time to propagate the change across servers
→ Then test again

### I don't see an ENABLE button
→ The API may already be enabled
→ Check if your API key has Custom Search API restrictions
→ Go to Credentials → Click your API key → Check "API restrictions"

### Still getting 403 after enabling
→ Create a NEW API key:
   1. Go to https://console.cloud.google.com/apis/credentials
   2. Click "+ CREATE CREDENTIALS" → API Key
   3. Copy the new key
   4. Update GOOGLE_CSE_API_KEY in .env
   5. Restart backend

### I have a billing account but still 403
→ Make sure Custom Search API quota is not exceeded
→ Go to https://console.cloud.google.com/apis/api/customsearch.googleapis.com/quotas
→ Check "Queries per day" quota

---

## Quick Status Check

Your current API credentials:
- API Key: AIzaSyBtHqADS99L-__Orq-ro7wu28Sjy_Xkl28 ✓ (valid format)
- Search Engine ID: c770bdc06ded44863 ✓ (valid format)
- Custom Search API: ✗ **DISABLED** ← **FIX THIS**
- Billing Account: No information available

**Next Action:**
Enable the API using the link above, then test with `debug_google_cse.py`
