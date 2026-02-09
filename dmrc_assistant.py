import os
import csv
import re
import logging
from pathlib import Path
from typing import List, Dict, Optional
import httpx
from openai import OpenAI
import difflib

# Load environment variables if python-dotenv used (optional)
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Configure logging
logger = logging.getLogger("dmrc_assistant")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Environment / config
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
GOOGLE_CSE_API_KEY = os.getenv("GOOGLE_CSE_API_KEY")       # Google Custom Search JSON API key
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")                # Programmable Search Engine ID (cx)
SERPAPI_KEY = os.getenv("SERPAPI_KEY")                    # fallback if you prefer
GOOGLE_SEARCH_TIMEOUT = float(os.getenv("GOOGLE_SEARCH_TIMEOUT", "6"))
OPENAI_TIMEOUT = float(os.getenv("OPENAI_TIMEOUT", "12"))

# If set, simulate live search results when external API keys are not available
SIMULATE_LIVE = os.getenv("ASSISTANT_SIMULATE_LIVE", "false").lower() in ("1", "true", "yes")

# Initialize OpenAI client (only if API key is available)
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY not set — OpenAI summarization will fail until provided.")

# Live keyword triggers
LIVE_KEYWORDS = ["today", "now", "closed", "delay", "delayed", "strike", "status", "running", "cancelled", "cancel", "holiday"]

# Safety threshold for local-match (simple token overlap)
LOCAL_MATCH_MIN_OVERLAP = 2

# CSV filenames (expected in project root)
INTENTS_CSV = Path(__file__).parent / "dmrc_chatbot_intents.csv"
STATIONS_CSV = Path(__file__).parent / "dmrc_master_stations.csv"

class DMRCAssistant:
    def __init__(self):
        self.intents = {}        # intent -> list(example strings)
        self.stations = {}       # station_name -> station record
        self.load_local_data()

        # local responses for known intents (extend as needed)
        self.local_responses = {
            "fare_enquiry": {
                "en": "To get exact fare, use the Route Finder and enter both stations. Smart card fares get a discount. If you provide start and end stations I can calculate an estimate.",
                "hi": "सटीक किराया प्राप्त करने के लिए 'रूट फाइंडर' में दोनों स्टेशन दर्ज करें। स्मार्ट कार्ड पर छूट लागू होती है।"
            },
            "last_train": {
                "en": "Metro last-train times vary by line. Typical last trains are between 10:30 PM and 11:45 PM. Give me the line or stations and I will check local data.",
                "hi": "लाइन के अनुसार आखिरी ट्रेन का समय बदलता है। अधिक जानकारी के लिए स्टेशन बताइए।"
            },
            "route_query": {
                "en": "Use the 'Find Route' feature or give me start and destination station names — I'll return stations, interchanges and fare estimate.",
                "hi": "कृपया शुरू और गंतव्य स्टेशन बताइए, मैं रूट, इंटरचेंज और किराया बताऊंगा।"
            },
            "lost_and_found": {
                "en": "Lost & Found office: Kashmere Gate Station. For fastest help contact Customer Care 155370 or visit the station.",
                "hi": "लॉस्ट एंड फाउंड: कश्मीरी गेट स्टेशन। मदद के लिए 155370 पर कॉल करें।"
            },
            "helpline": {
                "en": "Customer Care: 155370. For security CISF: 155655.",
                "hi": "कस्टमर केयर: 155370। सुरक्षा (CISF): 155655।"
            }
            # extend mapping as needed
        }

    # ------------------ Local data loading ------------------
    def load_local_data(self):
        # Load intents CSV
        if INTENTS_CSV.exists():
            try:
                with open(INTENTS_CSV, newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        intent = row.get("intent", "").strip()
                        query = row.get("example_query", "").strip().lower()
                        if not intent or not query:
                            continue
                        self.intents.setdefault(intent, []).append(query)
                logger.info(f"Loaded {sum(len(v) for v in self.intents.values())} intent examples ({len(self.intents)} intents)")
            except Exception as e:
                logger.exception("Failed to load intents CSV: %s", e)
        else:
            logger.warning(f"Intents CSV not found at {INTENTS_CSV}")

        # Load stations CSV (basic)
        if STATIONS_CSV.exists():
            try:
                with open(STATIONS_CSV, newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        name = row.get("station_name", "").strip()
                        if not name:
                            continue
                        lines = [l.strip() for l in row.get("lines", "").split(",") if l.strip()]
                        interchange = row.get("interchange", "").strip().lower() == "yes"
                        
                        # Capture all other columns as metadata (e.g., parking, lift, gates)
                        metadata = {k.lower(): v.strip() for k, v in row.items() 
                                   if k not in ["station_name", "lines", "interchange", "station_id"] and v and v.strip()}

                        self.stations[name.lower()] = {
                            "id": row.get("station_id", "").strip(),
                            "name": name,
                            "lines": lines,
                            "interchange": interchange,
                            "metadata": metadata
                        }
                logger.info(f"Loaded {len(self.stations)} stations from CSV")
            except Exception as e:
                logger.exception("Failed to load stations CSV: %s", e)
        else:
            logger.warning(f"Stations CSV not found at {STATIONS_CSV}")

    # ------------------ Matching / detection ------------------
    def is_dmrc_intent(self, user_query: str) -> Optional[str]:
        """Return intent name if local CSV suggests a match, else None.
        Uses the BEST match (highest token overlap), not first match."""
        msg = re.sub(r"[^\w\s]", " ", user_query.lower())
        msg_tokens = set(w for w in msg.split() if len(w) > 1)
        if not msg_tokens:
            return None
        
        best_intent = None
        best_overlap = 0
        
        for intent, examples in self.intents.items():
            for ex in examples:
                ex_tokens = set(w for w in ex.split() if len(w) > 1)
                overlap = len(ex_tokens & msg_tokens)
                if overlap >= LOCAL_MATCH_MIN_OVERLAP and overlap > best_overlap:
                    best_intent = intent
                    best_overlap = overlap
        
        return best_intent

    def contains_live_keyword(self, user_query: str) -> bool:
        q = user_query.lower()
        return any(k in q for k in LIVE_KEYWORDS)

    def simulate_search(self, q: str, num: int = 3) -> List[Dict]:
        """Return a small set of simulated search results when live APIs are not configured."""
        # Simple deterministic simulated results referencing local CSV or DMRC site
        results = []
        results.append({
            "title": "DMRC Service Update - Official Notice",
            "link": "https://www.delhimetrorail.com/notice/service-update",
            "snippet": f"Official notice related to: {q}. Please check the official DMRC site for latest updates."
        })
        results.append({
            "title": "DMRC Customer Care Advisory",
            "link": "https://www.delhimetrorail.com/customer-care",
            "snippet": "Customer care advisory and helpline details for commuters."
        })
        results.append({
            "title": "Local dataset: DMRC stations (local copy)",
            "link": str(STATIONS_CSV),
            "snippet": "Local dataset contains station lines and interchange flags." 
        })
        return results[:num]

    # ------------------ Station lookup helpers ------------------
    def normalize_station_key(self, name: str) -> str:
        return re.sub(r"\s+", " ", name.strip()).lower()

    def find_station_name_in_query(self, user_query: str) -> Optional[str]:
        """Try to find a station name mentioned in the user's query.
        Prefer longest match from local stations list; fallback to simple regex captures.
        """
        q = user_query.lower()
        # exact longest match from known stations
        candidates = []
        for s in self.stations.keys():
            if s in q:
                candidates.append(s)
        if candidates:
            # return longest match (more specific)
            return max(candidates, key=len)

        # regex captures for patterns like 'is X an interchange' or 'lines at X'
        patterns = [
            r"is\s+(.+?)\s+an\s+interchange",
            r"lines\s+(?:at|in)\s+(.+)",
            r"what\s+lines\s+(?:at|in)\s+(.+)",
            r"station\s+info\s+for\s+(.+)",
            r"info\s+on\s+(.+)"
        ]
        for p in patterns:
            m = re.search(p, user_query, re.IGNORECASE)
            if m:
                name = m.group(1).strip().strip('?.!')
                return self.normalize_station_key(name)

        return None

    def get_station_info(self, station_key: str) -> Optional[Dict]:
        """Return station info dict or None. station_key is normalized lower-case name."""
        if not station_key:
            return None
        # exact match
        rec = self.stations.get(station_key)
        if rec:
            return rec

        # substring match
        for k, v in self.stations.items():
            if station_key in k or k in station_key:
                return v

        # fuzzy match using difflib (best effort)
        keys = list(self.stations.keys())
        close = difflib.get_close_matches(station_key, keys, n=1, cutoff=0.7)
        if close:
            return self.stations.get(close[0])

        return None

    # ------------------ External search ------------------
    async def google_cse_search(self, q: str, num: int = 5) -> List[Dict]:
        if not GOOGLE_CSE_API_KEY or not GOOGLE_CSE_ID:
            raise RuntimeError("Google CSE credentials missing (GOOGLE_CSE_API_KEY / GOOGLE_CSE_ID).")

        params = {
            "key": GOOGLE_CSE_API_KEY,
            "cx": GOOGLE_CSE_ID,
            "q": f"{q} site:delhimetrorail.com",
            "num": str(num)
        }
        url = "https://www.googleapis.com/customsearch/v1"
        async with httpx.AsyncClient(timeout=GOOGLE_SEARCH_TIMEOUT) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            data = r.json()
        results = []
        for item in data.get("items", [])[:num]:
            results.append({
                "title": item.get("title"),
                "link": item.get("link"),
                "snippet": item.get("snippet")
            })
        return results

    async def serpapi_search(self, q: str, num: int = 5) -> List[Dict]:
        if not SERPAPI_KEY:
            raise RuntimeError("No SERPAPI_KEY available for fallback search.")
        params = {
            "engine": "google",
            "q": f"{q} site:delhimetrorail.com",
            "api_key": SERPAPI_KEY,
            "num": num
        }
        url = "https://serpapi.com/search.json"
        async with httpx.AsyncClient(timeout=GOOGLE_SEARCH_TIMEOUT) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            data = r.json()
        results = []
        for item in data.get("organic_results", [])[:num]:
            results.append({
                "title": item.get("title"),
                "link": item.get("link"),
                "snippet": item.get("snippet") or item.get("snippet_highlighted_terms")
            })
        return results

    # ------------------ OpenAI summarization ------------------
    def openai_summarize(self, user_query: str, search_results: List[Dict], language: str = "en") -> str:
        if not OPENAI_API_KEY or not openai_client:
            raise RuntimeError("OPENAI_API_KEY not set. Cannot summarize external results.")

        context_lines = []
        for i, r in enumerate(search_results, start=1):
            context_lines.append(f"{i}. {r.get('title')}\n{r.get('snippet')}\n{r.get('link')}")
        context = "\n\n".join(context_lines) if context_lines else "No search results."

        system_prompt = (
            "You are an assistant with strict instruction: answer only from the provided official DMRC search results. "
            "Do NOT hallucinate. If the answer is not present in the results, say you could not find official info and ask for clarification. "
            "Always include the source links (at least 1) in the answer. Keep the tone like an official DMRC helpdesk agent. "
            "When summarizing, produce a short factual answer and then list the sources (title - URL)."
        )
        user_prompt = (
            f"User question: {user_query}\n\n"
            f"Official search results (delhimetrorail.com):\n{context}\n\n"
            "Provide a concise answer (1-3 short paragraphs) and then list the sources used."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        resp = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            max_tokens=600,
            temperature=0.0,
            timeout=OPENAI_TIMEOUT
        )
        content = resp.choices[0].message.content.strip()
        return content

    # ------------------ Public pipeline ------------------
    def process_query(self, user_query: str, language: str = "en") -> Dict:
        if not user_query or not user_query.strip():
            return {
                "response": "Please provide your question.",
                "language": language,
                "used_local": False,
                "used_google": False,
                "intent": None,
                "sources": [],
                "log": "empty query"
            }

        # 2a) Station-specific quick checks (answer directly if user asked about a station)
        station_in_q = self.find_station_name_in_query(user_query)
        if station_in_q:
            st = self.get_station_info(station_in_q)
            if st:
                # Check if user is asking about specific metadata (parking, lift, etc.)
                q_lower = user_query.lower()
                metadata = st.get("metadata", {})
                
                # Dynamic lookup: check if query contains any column name present in metadata
                found_info = []
                for key, val in metadata.items():
                    # If column name (e.g. 'parking') is in query
                    if key in q_lower:
                        found_info.append(f"{key.title()}: {val}")
                
                if found_info:
                    # Specific info found (e.g. Parking: Yes)
                    resp = f"Station: {st.get('name')}\n" + "\n".join(found_info)
                else:
                    # Default station info
                    lines = st.get("lines", [])
                    interchange = st.get("interchange")
                    resp = f"Station: {st.get('name')}\nLines: {', '.join(lines)}\nInterchange: {'Yes' if interchange else 'No'}"
                    
                    # Hint about available extra info
                    if metadata:
                        available = ", ".join(metadata.keys())
                        resp += f"\n\n(I also have info about: {available})"

                return {
                    "response": resp,
                    "language": language,
                    "used_local": True,
                    "used_google": False,
                    "intent": "station_info",
                    "sources": [{"title": "Local DMRC stations", "link": str(STATIONS_CSV), "snippet": "Station lookup from local dataset"}],
                    "log": "answered station info from local CSV"
                }

        if self.contains_live_keyword(user_query):
            search_results = []
            used_google = False
            # If configured to simulate live results, prefer that (useful without API keys)
            if SIMULATE_LIVE:
                logger.info("ASSISTANT_SIMULATE_LIVE enabled — returning simulated search results")
                search_results = self.simulate_search(user_query, num=5)
                used_google = False
            else:
                try:
                    import asyncio
                    search_results = asyncio.run(self.google_cse_search(user_query, num=5))
                    used_google = True
                except Exception as e:
                    logger.info("Google CSE failed or not configured: %s", e)
                    try:
                        import asyncio
                        search_results = asyncio.run(self.serpapi_search(user_query, num=5))
                        used_google = True
                    except Exception as e2:
                        logger.warning("Fallback search failed: %s", e2)
                        search_results = []

            if not search_results:
                return {
                    "response": ("I could not find any official DMRC notice for your query. "
                                 "Would you like me to search wider (news/media) or provide your exact station/line/date?"),
                    "language": language,
                    "used_local": False,
                    "used_google": False,
                    "intent": None,
                    "sources": [],
                    "log": "no official search results found"
                }

            # Skip OpenAI summarization for speed — return raw search results directly
            lines = []
            for r in search_results[:3]:
                lines.append(f"{r.get('title')}\n{r.get('snippet')}\n{r.get('link')}\n")
            reply = "Here are the official DMRC search results I found:\n\n" + "\n\n".join(lines)
            return {
                "response": reply,
                "language": language,
                "used_local": False,
                "used_google": True,
                "intent": None,
                "sources": search_results,
                "log": "search results returned (OpenAI summarization disabled for speed)"
            }

        detected_intent = self.is_dmrc_intent(user_query)
        if detected_intent:
            resp_text = self.local_responses.get(detected_intent, {}).get(language)
            if resp_text:
                return {
                    "response": resp_text,
                    "language": language,
                    "used_local": True,
                    "used_google": False,
                    "intent": detected_intent,
                    "sources": [{"title": "Local DMRC dataset", "link": str(INTENTS_CSV), "snippet": "Answer from local intents dataset"}],
                    "log": "answered from local intents CSV"
                }
            return {
                "response": f"I detected intent '{detected_intent}' but no canned response is available. Please provide more details (stations, line) so I can help.",
                "language": language,
                "used_local": True,
                "used_google": False,
                "intent": detected_intent,
                "sources": [{"title": "Local DMRC dataset", "link": str(INTENTS_CSV), "snippet": "Intent matched but no canned text"}],
                "log": "intent matched, no canned response"
            }

        return {
            "response": ("I don't have a direct match in our local DMRC dataset for that question and it doesn't look like a live status query. "
                         "Could you please clarify: do you want station information, fare calculation (please give start and end stations), or helpline/contact details?"),
            "language": language,
            "used_local": False,
            "used_google": False,
            "intent": None,
            "sources": [],
            "log": "asked for clarification"
        }
