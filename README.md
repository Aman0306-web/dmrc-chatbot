# DMRC Metro Assistant - Delhi Metro Route & Information Chatbot

A FastAPI-based AI chatbot that provides **real-time** Delhi Metro information including route finding, station details, timings, fares, and live service updates.

## Features

✅ **Station Information** — Get details about any metro station (interchange status, lines serving it)  
✅ **Route Finding** — Find optimal routes between two stations with interchange counts and estimated fares  
✅ **Live Service Status** — Check for delays, strikes, closures, and service updates from official DMRC  
✅ **FAQ & Intent Matching** — Answer common questions about fares, timings, recharge, lost & found, etc.  
✅ **Multi-Language Support** — Hindi & English responses  
✅ **Google Custom Search** — Query official DMRC website for accurate information  
✅ **Responsive Web UI** — Clean React-like frontend with chat interface and route finder  

## Quick Setup

### 1. Install Dependencies

```bash
# Create a virtual environment
python -m venv .venv

# Activate it
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```ini
# OpenAI API (optional - currently disabled for speed)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# Google Custom Search API (optional)
GOOGLE_CSE_API_KEY=your_google_cse_api_key
GOOGLE_CSE_ID=your_programmable_search_engine_id

# Feature flags
ASSISTANT_SIMULATE_LIVE=true
```

**Note:** If API keys are not provided, the assistant will use simulated results (still works great for demos).

### 3. Run the Backend

```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs on: **http://localhost:8000**

### 4. Run the Frontend (in another terminal)

```bash
# Windows
python -m http.server 3000 --bind 127.0.0.1 --directory .

# macOS/Linux
python3 -m http.server 3000 --bind 127.0.0.1 --directory .
```

Frontend runs on: **http://localhost:3000**

### 5. Open in Browser

Visit: **http://localhost:3000/index-enhanced.html**

---

## API Endpoints

### Chat / Assistant Query
```
POST /assistant
Content-Type: application/json

{
  "query": "Is Kasturba Nagar an interchange?",
  "language": "en"
}

Response:
{
  "response": "Station: Kasturba Nagar\nLines: red, yellow, green, violet, pink, magenta, grey...",
  "language": "en",
  "used_local": true,
  "used_google": false,
  "intent": null,
  "sources": [ ... ],
  "log": "answered from local data"
}
```

### Route Finding
```
POST /route
Content-Type: application/json

{
  "from_station": "Rajiv Chowk",
  "to_station": "Connaught Place"
}

Response:
{
  "route": ["Rajiv Chowk", "Connaught Place"],
  "from_station": "Rajiv Chowk",
  "to_station": "Connaught Place",
  "num_stations": 1,
  "estimated_fare": "10"
}
```

### Get All Lines
```
GET /lines

Response:
{
  "lines": ["red", "yellow", "blue", "green", "violet", "pink", "magenta", "brown", "orange", "aqua", "grey"]
}
```

### Get Stations on a Line
```
GET /stations/red

Response:
{
  "line": "red",
  "stations": ["Rithala", "Kohat Enclave", ..., "Dilshad Garden"]
}
```

---

## Project Structure

```
DMRC 2026/
├── main.py                              # FastAPI backend server
├── dmrc_assistant.py                    # AI assistant with local + Google search
├── index-enhanced.html                  # Web UI (chat + route finder)
├── dmrc_chatbot_intents.csv             # Intent examples (42 Q&A patterns)
├── dmrc_stations_dataset.csv            # Station master data (82 stations)
├── routes/                              # Per-line station files
│   ├── red_route.csv
│   ├── blue_route.csv
│   └── ...
├── .env                                 # Configuration (API keys, feature flags)
├── requirements.txt                     # Python dependencies
├── package.json                         # Node.js metadata (optional)
└── README.md                            # This file
```

---

## Troubleshooting

### Google Custom Search API returning 403 Forbidden

**Symptom:** Google search endpoints fail with 403 error

**Fix:**
1. Get real Google Custom Search API key:
   - Visit: https://programmablesearchengine.google.com/
   - Create a **new** Programmable Search Engine (PSE) targeting `delhimetrorail.com`
   - Copy the **Engine ID (cx)** parameter
   - Go to: https://console.cloud.google.com/
   - Enable the **Custom Search API**
   - Create an API key in "Credentials"

2. Update `.env`:
   ```ini
   GOOGLE_CSE_API_KEY=your_new_api_key
   GOOGLE_CSE_ID=your_new_engine_id
   ASSISTANT_SIMULATE_LIVE=false
   ```

3. Restart the backend:
   ```bash
   # Kill existing uvicorn (Ctrl+C)
   # Then restart:
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

4. Test:
   ```bash
   curl -X POST http://localhost:8000/assistant \
     -H "Content-Type: application/json" \
     -d '{"query":"Is there a strike today?","language":"en"}'
   ```

### Backend won't start

- **Check port 8000 is free:** `netstat -ano | findstr :8000` (Windows)
- **Reload dependencies:** `pip install -r requirements.txt`
- **Clear Python cache:** `Remove-Item -Recurse __pycache__` (Windows)

### Frontend not loading

- **Check port 3000 is free:** `netstat -ano | findstr :3000` (Windows)
- **CORS errors:** Ensure backend is running on `http://localhost:8000`
- **Hard refresh browser:** `Ctrl+Shift+R` or clear cache

---

## Sample Queries

Try these in the chat interface:

1. **Station Info:** "Is Kasturba Nagar an interchange?"
2. **Route Finding:** "Route from Rajiv Chowk to Karol Bagh"
3. **FAQ:** "What are metro timings?" or "How much is the fare?"
4. **Live Status:** "Is there a strike today?" or "Any delays on the Blue Line?"
5. **Helpline:** "How do I contact DMRC?" or "Where is Lost & Found?"

---

## Development Notes

- **Backend Framework:** FastAPI (async Python)
- **Frontend:** HTML5 + Vanilla JavaScript (no build step needed)
- **Data Source:** CSV files for intents, stations, and routes
- **Search:** Google Custom Search API + optional simulated fallback
- **AI Summary:** OpenAI integration (disabled by default for speed)
- **Languages:** Hindi & English

---

## API Keys (Optional but Recommended)

### For Google Custom Search
1. Go to https://programmablesearchengine.google.com/
2. Create a new Programmable Search Engine for `delhimetrorail.com`
3. Copy the **Engine ID**
4. Go to https://console.cloud.google.com/ and enable **Custom Search API**
5. Create an **API Key** under Credentials
6. Add to `.env`

### For OpenAI (Advanced)
1. Go to https://platform.openai.com/account/api-keys
2. Create a new API key
3. Add to `.env`
4. To enable: Change `openai_summarize()` skip in `dmrc_assistant.py` (lines ~373)

---

## License

This is part of the DMRC Chatbot Project. For educational purposes.

---

## Support

For issues or questions:
- Check the troubleshooting section above
- Review error logs in the terminal
- Verify `.env` configuration
- Ensure all ports (8000, 3000) are free
