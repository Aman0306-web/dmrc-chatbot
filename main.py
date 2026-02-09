from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from collections import defaultdict, deque
from typing import Dict
import uvicorn
import csv
import os
from pathlib import Path
import logging

# Import enhanced modules
try:
    import routing
    from station_loader import StationLoader
    STATION_LOADER = StationLoader("dmrc_master_stations.csv")
except Exception as e:
    print(f"⚠️ StationLoader/Routing failed to load: {e}")
    STATION_LOADER = None

try:
    from fuzzy_search import fuzzy_search_station, autocomplete_station, best_match_station
    FUZZY_SEARCH_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Fuzzy search failed to load: {e}")
    FUZZY_SEARCH_AVAILABLE = False

# Optional assistant integration
try:
    from dmrc_assistant import DMRCAssistant
except Exception:
    DMRCAssistant = None
app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    simulate = os.getenv("ASSISTANT_SIMULATE_LIVE", "false").lower() in ("true", "1", "yes")
    
    # Sync METRO_DATA with CSV if available (Connects Backend Logic to Data File)
    if STATION_LOADER:
        print("🔄 Syncing METRO_DATA from StationLoader CSV...")
        updates = 0
        for line_name, stations in STATION_LOADER.lines_index.items():
            # Normalize key: "Red Line" -> "red", "Airport Express" -> "airport_express"
            key = line_name.lower().replace(" ", "_")
            
            if key in METRO_DATA:
                METRO_DATA[key]["stations"] = stations
                updates += 1
            else:
                # Add new line found in CSV
                METRO_DATA[key] = {
                    "name": line_name.title(),
                    "color": "#808080", # Default color for new lines
                    "stations": stations,
                    "first_train": "06:00 AM",
                    "last_train": "11:00 PM"
                }
                updates += 1
        
        _STATION_LOOKUP.clear()
        for line_data in METRO_DATA.values():
            for s in line_data["stations"]:
                _STATION_LOOKUP[s.strip().lower()] = s
                
        print(f"✅ Synced {updates} lines from CSV to internal METRO_DATA")

    print("\n" + "="*60)
    print(f"🚀 DMRC MetroSahayak Backend Running")
    print(f"🔧 Mode: {'SIMULATION (Fix Applied)' if simulate else 'LIVE API'}")
    print(f"📂 Docs: http://localhost:8000/docs")
    print("="*60 + "\n")

# ==================== DATA STRUCTURES ====================

METRO_DATA = {
    "red": {
        "name": "Red Line",
        "color": "#DC143C",
        "stations": [
            "Dilshad Garden", "Shahbad Dairy", "Shalimar Bagh", "Ashok Vihar",
            "Punjabi Bagh", "Inder Lok", "Kanhaiya Nagar", "Kasturba Nagar",
            "Lajpat Nagar", "Jangpura", "Karol Bagh", "New Delhi",
            "Chawri Bazaar", "Chandni Chowk", "Kashmere Gate", "Civil Lines",
            "Old Delhi", "Netaji Subhas Place"
        ],
        "first_train": "5:30 AM",
        "last_train": "11:30 PM"
    },
    "yellow": {
        "name": "Yellow Line",
        "color": "#FFD700",
        "stations": [
            "Samaypur Badli", "Rohini Sector 18", "Rohini Sector 16", "Rohini Sector 15",
            "Netaji Subhas Place", "Kasturba Nagar", "Pul Bangash", "Chandni Chowk",
            "Chawri Bazaar", "New Delhi", "Rajiv Chowk", "Patel Chowk",
            "Central Secretariat", "Udyog Bhawan", "South Extension", "Lodi Garden",
            "Amar Colony", "Kalkaji Mandir", "Govind Puri", "Okhla Vihar",
            "Jamia Millia Islamia", "Sukhdev Vihar", "Badarpur Border"
        ],
        "first_train": "5:45 AM",
        "last_train": "11:15 PM"
    },
    "blue": {
        "name": "Blue Line",
        "color": "#4169E1",
        "stations": [
            "Noida City Center", "Noida Electronic City", "Noida Sector 16",
            "Noida Sector 18", "Noida Sector 34/Sector 52", "Noida Central",
            "South Ex", "Dwarka Sector 8", "Dwarka Sector 9",
            "Dwarka Sector 11", "Dwarka Sector 12", "Dwarka Sector 14", "Dwarka",
            "Rajiv Chowk", "Barakhamba Road", "Mandi House", "Pragati Maidan"
        ],
        "first_train": "5:00 AM",
        "last_train": "11:45 PM"
    },
    "green": {
        "name": "Green Line",
        "color": "#228B22",
        "stations": [
            "Brigadier Hoshiar Singh", "Estakada", "Mayur Vihar Phase 1",
            "Mayur Vihar Extension", "Greater Kailash", "Kalkaji Mandir",
            "Nehru Enclave", "Khanpur", "Ankur", "Botanical Garden",
            "Indraprastha", "Chawri Bazaar", "Kasturba Nagar", "Lajpat Nagar"
        ],
        "first_train": "6:00 AM",
        "last_train": "11:00 PM"
    },
    "violet": {
        "name": "Violet Line",
        "color": "#8B00FF",
        "stations": [
            "Kasturba Nagar", "Ashok Vihar", "Mukherjee Nagar", "Shastri Nagar",
            "Chandni Chowk", "Chawri Bazaar", "New Delhi", "Patel Chowk",
            "Central Secretariat", "Khan Market", "JLN Stadium", "Lajpat Nagar",
            "Moolchand", "Kalkaji Mandir", "Govind Puri"
        ],
        "first_train": "5:50 AM",
        "last_train": "11:20 PM"
    },
    "pink": {
        "name": "Pink Line",
        "color": "#FF69B4",
        "stations": [
            "Majlis Park", "Azadpur", "Shalimar Bagh", "Netaji Subhas Place",
            "Inder Lok", "Kanhaiya Nagar", "Kasturba Nagar", "Mandi House",
            "Barakhamba Road", "Rajiv Chowk", "Patel Chowk", "Lajpat Nagar",
            "South Extension", "Mayur Vihar Phase 1", "Mayur Vihar Extension"
        ],
        "first_train": "5:45 AM",
        "last_train": "11:15 PM"
    },
    "magenta": {
        "name": "Magenta Line",
        "color": "#FF00FF",
        "stations": [
            "Botanical Garden", "Okhla Vihar", "Sukhdev Vihar", "Jamia Millia Islamia",
            "Munirka", "Chhatarpur", "Mehrauli", "Chhattarpur", "Kalkaji Mandir",
            "Greater Kailash", "Lajpat Nagar", "Khan Market", "Mandi House",
            "Delhi Gate", "Chandni Chowk", "Kasturba Nagar", "Inder Lok",
            "Netaji Subhas Place"
        ],
        "first_train": "5:30 AM",
        "last_train": "11:40 PM"
    },
    "grey": {
        "name": "Grey Line",
        "color": "#808080",
        "stations": [
            "Dwarka", "Dwarka Sector 14", "Dwarka Sector 13", "Dwarka Sector 12",
            "Dwarka Sector 11", "Dwarka Sector 10", "Dwarka Sector 9", "Dwarka Sector 8",
            "South Ex", "Rajiv Chowk", "Chawri Bazaar", "Chandni Chowk",
            "Kasturba Nagar"
        ],
        "first_train": "6:00 AM",
        "last_train": "11:00 PM"
    },
    "airport_express": {
        "name": "Airport Express",
        "color": "#FF6347",
        "stations": [
            "New Delhi", "Shivaji Stadium", "Pragati Maidan", "Indraprastha",
            "Hazrat Nizamuddin", "Aerocity", "Terminal 3", "Terminal 1", "Terminal 2"
        ],
        "first_train": "5:30 AM",
        "last_train": "11:30 PM"
    }
}

# Station Interchange Mapping
INTERCHANGES = {
    "Rajiv Chowk": ["blue", "yellow", "violet", "pink"],
    "New Delhi": ["red", "yellow", "airport_express"],
    "Chandni Chowk": ["red", "yellow", "violet", "magenta"],
    "Kasturba Nagar": ["red", "pink", "magenta"],
    "Kashmere Gate": ["red"],
    "Chawri Bazaar": ["red", "yellow", "magenta"],
    "Lajpat Nagar": ["yellow", "violet", "pink", "magenta"],
    "Patel Chowk": ["yellow", "violet", "pink"],
    "Central Secretariat": ["yellow", "violet"],
    "Kalkaji Mandir": ["yellow", "green", "magenta"],
    "Dwarka": ["blue", "grey"],
    "Indraprastha": ["green", "airport_express"],
    "Mandi House": ["pink", "magenta"],
    "Khan Market": ["violet", "magenta"],
    "Mayur Vihar Phase 1": ["green", "pink"],
    "Greater Kailash": ["green", "magenta"],
    "Netaji Subhas Place": ["red", "pink", "magenta"],
    "Barakhamba Road": ["blue", "pink"],
    "South Extension": ["yellow", "pink"],
    "Inder Lok": ["red", "pink", "magenta"],
}

# Station Facilities Database (unchanged)
STATION_FACILITIES = {
    "Kashmere Gate": {
        "gates": ["Gate A", "Gate B", "Gate C"],
        "landmarks": "Old Delhi Railway Station, Red Fort",
        "lost_found": True,
        "restrooms": True,
        "parking": True
    },
    "New Delhi": {
        "gates": ["Gate 1", "Gate 2", "Gate 3"],
        "landmarks": "New Delhi Railway Station, Connaught Place",
        "lost_found": True,
        "restrooms": True,
        "parking": True
    },
    "Rajiv Chowk": {
        "gates": ["Gate A", "Gate B"],
        "landmarks": "Connaught Place, Palika Bazaar",
        "lost_found": True,
        "restrooms": True,
        "parking": False
    },
    "Chandni Chowk": {
        "gates": ["Gate 1", "Gate 2"],
        "landmarks": "Chandni Chowk Market, Jama Masjid",
        "lost_found": True,
        "restrooms": True,
        "parking": False
    }
}

# Fare Structure (unchanged)
FARE_SLABS = {
    1: 10,
    2: 10,
    3: 15,
    4: 15,
    5: 20,
    6: 20,
    7: 25,
    8: 25,
    9: 30,
    10: 30,
    11: 35,
    12: 35,
    13: 40,
    14: 40,
    15: 45,
    16: 45,
    17: 50,
    18: 50,
    19: 55,
    20: 55,
}

# Help Content (unchanged)
HELP_CONTENT = {
    "ticket_not_working": {
        "en": "Your ticket/card is not working. Please:\n1. Check if the card is properly inserted\n2. Visit the nearest Help Desk (Gate area)\n3. Call Customer Care: 155370\n4. You may get a replacement card",
        "hi": "आपकी टिकट/कार्ड काम नहीं कर रही है। कृपया:\n1. चेक करें कि कार्ड सही तरीके से डाला गया है\n2. निकटतम हेल्प डेस्क पर जाएं\n3. कस्टमर केयर को कॉल करें: 155370\n4. आपको प्रतिस्थापन कार्ड मिल सकता है"
    },
    "lost_token": {
        "en": "You lost your Metro token/card?\n1. Visit Lost & Found at Kashmere Gate Station\n2. Or call: 155370\n3. You can report within 30 days\n4. Fee: ₹50 for replacement",
        "hi": "आपकी मेट्रो टोकन/कार्ड खो गई?\n1. कश्मीरी गेट स्टेशन पर Lost & Found पर जाएं\n2. या कॉल करें: 155370\n3. आप 30 दिन में रिपोर्ट कर सकते हैं\n4. शुल्क: प्रतिस्थापन के लिए ₹50"
    },
    "low_balance": {
        "en": "Your card balance is low. You can:\n1. Recharge at any Metro station ticket counter\n2. Use online recharge apps (DMRC website)\n3. Minimum balance required: ₹10\n4. Max value per card: ₹2000",
        "hi": "आपके कार्ड में बैलेंस कम है। आप कर सकते हैं:\n1. किसी भी मेट्रो स्टेशन टिकट काउंटर पर रीचार्ज करें\n2. ऑनलाइन रीचार्ज ऐप्स का उपयोग करें\n3. न्यूनतम बैलेंस आवश्यक: ₹10\n4. कार्ड के लिए अधिकतम मूल्य: ₹2000"
    },
    "overstay": {
        "en": "You've stayed in the metro system beyond the ticket validity:\n1. You'll be charged a penalty fare\n2. Exit and pay the additional amount at the gate\n3. Current exit fare depends on your entry point\n4. Save your receipts for reference",
        "hi": "आप मेट्रो सिस्टम में टिकट की वैधता से अधिक समय रहे हैं:\n1. आपको पेनल्टी किराया लगेगा\n2. गेट पर अतिरिक्त राशि का भुगतान करें\n3. वर्तमान निकास किराया आपके प्रवेश बिंदु पर निर्भर करता है\n4. संदर्भ के लिए अपनी रसीदें सहेजें"
    },
    "emergency": {
        "en": "Emergency Contacts:\n• Customer Care: 155370\n• CISF (Security): 155655\n• Lost & Found: Kashmere Gate\n• Women Safety: Dial 155370\n• Medical: 155370",
        "hi": "आपातकालीन संपर्क:\n• कस्टमर केयर: 155370\n• सीआईएसएफ (सुरक्षा): 155655\n• खोई हुई चीजें: कश्मीरी गेट\n• महिला सुरक्षा: 155370 डायल करें\n• चिकित्सा: 155370"
    }
}

# Build case-insensitive station lookup map
_STATION_LOOKUP = {}
for line_data in METRO_DATA.values():
    for s in line_data["stations"]:
        _STATION_LOOKUP[s.strip().lower()] = s  # map lowercase -> canonical

def normalize_station(name: str):
    if not name:
        return None
    key = name.strip().lower()
    return _STATION_LOOKUP.get(key)

# ==================== PYDANTIC MODELS ====================

class ChatMessage(BaseModel):
    message: str
    language: str = "en"

class RouteQuery(BaseModel):
    from_station: str
    to_station: str
    language: str = "en"

# ==================== CHATBOT LOGIC ====================

class ChatbotEngine:
    def __init__(self):
        self.help_keywords = {
            "ticket": "ticket_not_working",
            "card": "ticket_not_working",
            "not working": "ticket_not_working",
            "lost": "lost_token",
            "token": "lost_token",
            "balance": "low_balance",
            "recharge": "low_balance",
            "overstay": "overstay",
            "stay": "overstay",
            "emergency": "emergency",
            "help": "emergency",
            "contact": "emergency",
        }
        
        # Load intents from CSV
        self.intents = {}
        self.load_intents_from_csv()
    
    def load_intents_from_csv(self):
        """Load chatbot intents from CSV file"""
        csv_path = Path(__file__).parent / "dmrc_chatbot_intents_expanded.csv"
        
        if csv_path.exists():
            try:
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        intent = row['intent'].strip()
                        query = row['example_query'].strip().lower()
                        
                        if intent not in self.intents:
                            self.intents[intent] = []
                        self.intents[intent].append(query)
                
                print(f"✅ Loaded {len(self.intents)} intents from CSV")
            except Exception as e:
                print(f"⚠️ Error loading CSV: {e}")
        else:
            print(f"⚠️ CSV file not found at {csv_path}")

    def get_response(self, message: str, language: str = "en") -> str:
        message_lower = message.lower()

        # Check for help topics in keywords
        for keyword, topic in self.help_keywords.items():
            if keyword in message_lower:
                return HELP_CONTENT[topic][language]

        # Check CSV-based intents
        matched_intent = self.match_intent(message_lower)
        if matched_intent:
            return self.get_intent_response(matched_intent, language)

        # Default greeting/info response
        if language == "hi":
            return "नमस्ते! मैं MetroSahayak हूं, आपका दिल्ली मेट्रो सहायक। मैं मदद कर सकता हूं:\n• रूट खोजना\n• किराया की गणना करना\n• स्टेशन की जानकारी\n• आपातकालीन संपर्क\nकृपया अपना प्रश्न पूछें।"
        else:
            return "Hello! I'm MetroSahayak, your Delhi Metro assistant. I can help with:\n• Finding routes\n• Calculating fares\n• Station information\n• Emergency contacts\nPlease ask your question."

    def match_intent(self, message_lower: str) -> str:
        """Match user message to an intent based on CSV data"""
        for intent, queries in self.intents.items():
            for query in queries:
                # Check if key words from example match
                query_words = set(query.split())
                message_words = set(message_lower.split())
                
                # If at least 2 words match, consider it a match
                if len(query_words & message_words) >= 2:
                    return intent
        
        return None

    def get_intent_response(self, intent: str, language: str = "en") -> str:
        """Get response based on matched intent"""
        responses = {
            "fare_enquiry": {
                "en": "💰 To find metro fares:\n• Fares are based on distance\n• Check the route details for exact fare\n• Smart cards get 10% discount\n• Off-peak fares (10 AM-5 PM) are discounted",
                "hi": "💰 मेट्रो किराया जानने के लिए:\n• किराया दूरी पर आधारित है\n• सटीक किराए के लिए रूट विवरण देखें\n• स्मार्ट कार्ड को 10% छूट मिलती है\n• ऑफ-पीक किराया (10 AM-5 PM) घटा हुआ होता है"
            },
            "last_train": {
                "en": "🕐 Last Train Timings:\n• Most lines: 10:30 PM - 11:30 PM\n• Some lines: 10:00 PM - 11:00 PM\n• Check specific line for exact timing\n• Weekend: Sometimes earlier",
                "hi": "🕐 आित्मी ट्रेन समय:\n• अधिकांश लाइनें: 10:30 PM - 11:30 PM\n• कुछ लाइनें: 10:00 PM - 11:00 PM\n• सटीक समय के लिए विशिष्ट लाइन देखें\n• सप्ताहांत: कभी-कभी जल्दी"
            },
            "route_query": {
                "en": "🗺️ To find the best route:\n• Use the 'Find Route' section\n• Enter starting and destination stations\n• You'll get stations and fare details\n• Interchange stations will be highlighted",
                "hi": "🗺️ सबसे अच्छा रूट खोजने के लिए:\n• 'रूट खोजें' अनुभाग का उपयोग करें\n• शुरुआती और गंतव्य स्टेशन दर्ज करें\n• आपको स्टेशन और किराया विवरण मिलेगा\n• इंटरचेंज स्टेशन हाइलाइट किए जाएंगे"
            },
            "lost_and_found": {
                "en": "📦 Lost & Found:\n• Main office: Kashmere Gate Station\n• Call: 155370\n• Hours: 8:00 AM - 8:00 PM (Mon-Sat)\n• Items kept for 3 months\n• File a written complaint at station",
                "hi": "📦 खोई हुई चीजें:\n• मुख्य कार्यालय: कश्मीरी गेट स्टेशन\n• कॉल करें: 155370\n• समय: 8:00 AM - 8:00 PM (सोमवार-शनिवार)\n• आइटम 3 महीने रखे जाते हैं\n• स्टेशन पर लिखित शिकायत दर्ज करें"
            },
            "helpline": {
                "en": "☎️ DMRC Helpline & Contact:\n• Customer Care: 155370\n• CISF Security: 155655\n• Lost & Found: Kashmere Gate\n• Women Safety: 155370\n• Medical: 155370\n• Website: www.delhimetrorail.com",
                "hi": "☎️ DMRC हेल्पलाइन:\n• कस्टमर केयर: 155370\n• सीआईएसएफ सुरक्षा: 155655\n• खोई हुई चीजें: कश्मीरी गेट\n• महिला सुरक्षा: 155370\n• चिकित्सा: 155370\n• वेबसाइट: www.delhimetrorail.com"
            },
            "metro_timings": {
                "en": "🕐 Metro Operating Hours:\n• Monday-Saturday: 6:00 AM - 11:00 PM\n• Sunday: 6:00 AM - 10:00 PM\n• First train: ~5:00-6:00 AM\n• Last train: ~10:30-11:30 PM\n• Varies by line",
                "hi": "🕐 मेट्रो का समय:\n• सोमवार-शनिवार: 6:00 AM - 11:00 PM\n• रविवार: 6:00 AM - 10:00 PM\n• पहली ट्रेन: ~5:00-6:00 AM\n• आखिरी ट्रेन: ~10:30-11:30 PM\n• लाइन के अनुसार भिन्न"
            },
            "recharge": {
                "en": "💳 Metro Card Recharge:\n• At station counters & TVM\n• Online: DMRC app, Paytm, PhonePe\n• Mobile wallets accepted\n• Minimum: ₹100\n• Maximum: ₹3000\n• Instant processing",
                "hi": "💳 मेट्रो कार्ड रीचार्ज:\n• स्टेशन काउंटर और TVM पर\n• ऑनलाइन: DMRC ऐप, Paytm, PhonePe\n• मोबाइल वॉलेट स्वीकार\n• न्यूनतम: ₹100\n• अधिकतम: ₹3000\n• तत्काल प्रसंस्करण"
            },
            "airport": {
                "en": "✈️ Airport Metro Connection:\n• Orange Line: New Delhi → Terminal 3\n• Travel time: ~20 minutes\n• Frequency: Every 10-15 minutes\n• Fare: ₹60\n• Luggage space available",
                "hi": "✈️ एयरपोर्ट मेट्रो:\n• ऑरेंज लाइन: नई दिल्ली → टर्मिनल 3\n• यात्रा का समय: ~20 मिनट\n• आवृत्ति: प्रत्येक 10-15 मिनट\n• किराया: ₹60\n• सामान स्थान उपलब्ध"
            },
            "rules": {
                "en": "⚠️ Metro Rules:\n❌ Prohibited: Smoking, eating, drinking, loud music\n✅ Allowed: 2 luggage (25kg each), folded bikes\n⚖️ Penalties: Up to ₹500\n👮 Help: Contact staff at gate\n📑 Safety: Follow all regulations",
                "hi": "⚠️ मेट्रो नियम:\n❌ प्रतिबंधित: धूम्रपान, खाना, पीना, तेज संगीत\n✅ अनुमत: 2 सामान (प्रत्येक 25kg), तहदार बाइक\n⚖️ जुर्माना: ₹500 तक\n👮 मदद: गेट पर स्टाफ से संपर्क करें"
            },
            "wifi": {
                "en": "📶 Delhi Metro WiFi:\n• Available at all underground stations\n• Free WiFi service\n• Search 'DelhiMetro-Wifi'\n• Speed: Good for browsing\n• Duration: Full journey",
                "hi": "📶 दिल्ली मेट्रो WiFi:\n• सभी भूमिगत स्टेशन पर उपलब्ध\n• मुफ्त WiFi सेवा\n• 'DelhiMetro-Wifi' खोजें\n• गति: ब्राउजिंग के लिए अच्छी\n• अवधि: पूरी यात्रा"
            },
            "parking": {
                "en": "🅿️ Metro Parking:\n• Available at major stations\n• Cars: ₹40 for first 4 hours\n• Bikes: ₹20 for first 4 hours\n• CCTV surveillance\n• Secure facilities\n• Park & Ride available",
                "hi": "🅿️ मेट्रो पार्किंग:\n• प्रमुख स्टेशन पर उपलब्ध\n• कार: पहले 4 घंटे ₹40\n• बाइक: पहले 4 घंटे ₹20\n• CCTV निगरानी\n• सुरक्षित सुविधाएं\n• पार्क एंड राइड उपलब्ध"
            },
            "smart_card": {
                "en": "💳 Smart Card Benefits:\n• Reusable & rechargeable\n• 10% discount on fares\n• Fast entry/exit\n• Deposit: ₹50 (refundable)\n• Validity: 10 years\n• No need to buy tokens",
                "hi": "💳 स्मार्ट कार्ड लाभ:\n• पुन: उपयोग करने योग्य\n• किराए पर 10% छूट\n• तेज प्रवेश/निकास\n• डिपोजिट: ₹50 (रिफंडेबल)\n• वैधता: 10 साल\n• टोकन खरीदने की जरूरत नहीं"
            },
            "peak_hours": {
                "en": "📊 Peak Hours:\n🔺 Morning: 8:00-10:00 AM\n🔺 Evening: 5:00-8:00 PM\n✅ Off-peak: 10:00 AM-5:00 PM (10% discount)\n💡 Travel light, avoid peak hours",
                "hi": "📊 पीक आवर्स:\n🔺 सुबह: 8:00-10:00 AM\n🔺 शाम: 5:00-8:00 PM\n✅ ऑफ-पीक: 10:00 AM-5:00 PM (10% छूट)\n💡 हल्का सामान, पीक आवर्स से बचें"
            },
            "interchange": {
                "en": "🔄 Interchange Stations:\n• Rajiv Chowk: Blue, Yellow, Violet, Pink\n• Chandni Chowk: Red, Yellow, Violet, Magenta\n• New Delhi: Red, Yellow, Airport Express\n• Central Secretariat: Yellow, Violet\n• Follow signage for smooth transfer",
                "hi": "🔄 इंटरचेंज स्टेशन:\n• राजीव चौक: नीली, पीली, बैंगनी, गुलाबी\n• चांदनी चौक: लाल, पीली, बैंगनी, मैजेंटा\n• नई दिल्ली: लाल, पीली, एयरपोर्ट एक्सप्रेस\n• सेंट्रल सेक्रेटेरिएट: पीली, बैंगनी\n• सुगम हस्तांतरण के लिए संकेत का पालन करें"
            }
        }
        
        return responses.get(intent, {}).get(language, "I can help you with metro information. Please ask a specific question.")

    def calculate_fare(self, num_stations: int) -> Dict:
        """Calculate fare based on number of stations"""
        distance = max(1, num_stations - 1)
        base_fare = FARE_SLABS.get(distance, 60)

        # Off-peak discount (10%)
        off_peak_fare = int(base_fare * 0.9)

        # Smart card discount (5%)
        smart_card_fare = int(base_fare * 0.95)

        return {
            "base_fare": base_fare,
            "off_peak_fare": off_peak_fare,
            "smart_card_fare": smart_card_fare,
            "minimum_fare": 10,
            "maximum_fare": 60,
            "currency": "₹"
        }

chatbot = ChatbotEngine()

# Initialize DMRCAssistant if available (safe fallback)
assistant = None
if DMRCAssistant is not None:
    try:
        assistant = DMRCAssistant()
        print("✅ DMRCAssistant initialized")
    except Exception as e:
        print("⚠️ Failed to initialize DMRCAssistant:", e)
# ==================== API ENDPOINTS ====================

# minimal logger for endpoint errors
logger = logging.getLogger("main")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

@app.get("/")
def read_root():
    return {
        "name": "MetroSahayak",
        "version": "1.0.0",
        "status": "running",
        "features": ["route_finding", "fare_calculation", "station_info", "emergency_contacts"]
    }

@app.post("/chat")
def chat(msg: ChatMessage):
    # Prefer DMRCAssistant if available
    if assistant is not None:
        try:
            result = assistant.process_query(msg.message, msg.language)
            # Ensure result is a dict with at least response/language
            if isinstance(result, dict) and "response" in result:
                return result
        except Exception as e:
            print("⚠️ DMRCAssistant processing failed:", e)

    # Fallback to original chatbot
    response = chatbot.get_response(msg.message, msg.language)
    return {
        "response": response,
        "language": msg.language
    }


class AssistantQuery(BaseModel):
    query: str
    language: str = "en"


@app.post("/assistant")
def assistant_endpoint(payload: AssistantQuery):
    """
    Endpoint: POST /assistant
    Body: { "query": "...", "language": "en" }
    Returns assistant result (response, sources, flags)
    """
    if assistant is None:
        raise HTTPException(status_code=503, detail="Assistant not available")
    try:
        result = assistant.process_query(payload.query, payload.language)
        safe_result = {
            "response": result.get("response"),
            "language": result.get("language"),
            "used_local": result.get("used_local"),
            "used_google": result.get("used_google"),
            "intent": result.get("intent"),
            "sources": result.get("sources", []),
            "log": result.get("log", "processed"),
        }
        return safe_result
    except Exception as e:
        logger.exception("Assistant endpoint error: %s", e)
        raise HTTPException(status_code=500, detail="Internal assistant error")


# ==================== ROUTE HELPER FUNCTIONS ====================

def get_station_lines(station: str):
    """Get all lines that pass through a station"""
    lines = []
    for line_code, line_data in METRO_DATA.items():
        if station in line_data["stations"]:
            lines.append(line_code)
    return lines


def get_line_name(line_code: str):
    """Get human-readable line name"""
    line_names = {
        "red": "Red Line",
        "yellow": "Yellow Line",
        "blue": "Blue Line",
        "green": "Green Line",
        "violet": "Violet Line",
        "pink": "Pink Line",
        "magenta": "Magenta Line",
        "grey": "Grey Line",
        "airport_express": "Airport Express"
    }
    return line_names.get(line_code, line_code.replace("_", " ").title())


def get_route_tips(num_stations: int, num_interchanges: int):
    """Generate helpful tips for the journey"""
    tips = []
    
    if num_interchanges == 0:
        tips.append("✓ No interchange needed - straight line journey!")
    elif num_interchanges == 1:
        tips.append(f"⚠ One interchange required at {num_interchanges} station")
    else:
        tips.append(f"⚠ Multiple interchanges ({num_interchanges}) - allow extra time")
    
    if num_stations > 10:
        tips.append("💡 This is a long journey - consider having some water/snacks")
    
    if num_stations > 1 and num_stations <= 3:
        tips.append("✓ Short journey - usually takes 5-10 minutes")
    
    return tips


@app.post("/route")
def find_route(query: RouteQuery):
    """
    Enhanced route finding with:
    - Station-by-station navigation with line info
    - Clear interchange instructions
    - Fare calculation
    - Travel time estimates
    """
    # Normalize station names (case-insensitive)
    from_st_raw = query.from_station
    to_st_raw = query.to_station

    from_st = normalize_station(from_st_raw)
    to_st = normalize_station(to_st_raw)

    if not from_st:
        raise HTTPException(status_code=404, detail=f"From station '{from_st_raw}' not found")
    if not to_st:
        raise HTTPException(status_code=404, detail=f"To station '{to_st_raw}' not found")

    if from_st == to_st:
        raise HTTPException(status_code=400, detail="From and To stations are the same")

    # Find shortest path using routing module
    path = routing.bfs_shortest_path(STATION_LOADER.graph, from_st, to_st)

    if not path:
        raise HTTPException(status_code=404, detail="No route found between these stations")

    stations = path
    num_stations = len(path)
    
    # Calculate fare
    fare = chatbot.calculate_fare(num_stations)

    # Identify connecting lines for each adjacent pair of stations
    edge_lines = []
    for i in range(len(stations) - 1):
        current_st = stations[i]
        next_st = stations[i + 1]
        
        current_lines = get_station_lines(current_st)
        next_lines = get_station_lines(next_st)
        
        # Find the line connecting these two stations
        connecting_line = None
        for line_code in current_lines:
            if line_code in next_lines:
                # Verify adjacency on this line
                line_stations = METRO_DATA[line_code]["stations"]
                if current_st in line_stations and next_st in line_stations:
                    curr_idx = line_stations.index(current_st)
                    next_idx = line_stations.index(next_st)
                    if abs(curr_idx - next_idx) == 1:
                        connecting_line = line_code
                        break
        
        # Fallback to first common line if strict adjacency fails
        if not connecting_line and current_lines and next_lines:
            connecting_line = list(set(current_lines) & set(next_lines))[0]
        
        edge_lines.append(connecting_line)

    # Build segments by grouping consecutive edges on same line
    segments = []
    if edge_lines:
        current_line = edge_lines[0]
        segment_start = 0
        
        for i in range(1, len(edge_lines)):
            if edge_lines[i] != current_line:
                # Line change detected - create segment
                segment_end = i
                segments.append({
                    "line": current_line,
                    "line_name": get_line_name(current_line),
                    "start_station": stations[segment_start],
                    "end_station": stations[segment_end],
                    "stations": stations[segment_start:segment_end + 1],
                    "station_count": segment_end - segment_start + 1,
                    "is_start": (segment_start == 0),
                    "is_interchange": (segment_start > 0)
                })
                current_line = edge_lines[i]
                segment_start = i
        
        # Add final segment
        segment_end = len(edge_lines)
        segments.append({
            "line": current_line,
            "line_name": get_line_name(current_line),
            "start_station": stations[segment_start],
            "end_station": stations[segment_end],
            "stations": stations[segment_start:segment_end + 1],
            "station_count": segment_end - segment_start + 1,
            "is_start": (segment_start == 0),
            "is_interchange": (segment_start > 0)
        })

    # Build interchange list
    interchanges = []
    for i in range(1, len(segments)):
        prev_segment = segments[i - 1]
        curr_segment = segments[i]
        interchange_station = prev_segment["end_station"]
        
        interchanges.append({
            "station": interchange_station,
            "from_line": prev_segment["line_name"],
            "from_line_code": prev_segment["line"],
            "to_line": curr_segment["line_name"],
            "to_line_code": curr_segment["line"],
            "instruction": f"At {interchange_station}, change from {prev_segment['line_name']} to {curr_segment['line_name']}"
        })
    
    # Travel time estimation (average 1.5 minutes per station)
    estimated_minutes = (num_stations - 1) * 1.5
    
    response = {
        "from_station": from_st,
        "to_station": to_st,
        "total_stations": num_stations,
        "stations": stations,
        "distance_stations": num_stations - 1,
        "estimated_travel_time_minutes": round(estimated_minutes, 1),
        "segments": segments,
        "interchanges": interchanges,
        "num_interchanges": len(interchanges),
        "fare": fare,
        "language": query.language,
        "tips": get_route_tips(num_stations, len(interchanges))
    }

    return response

@app.get("/lines")
def get_lines():
    lines = []
    for key, data in METRO_DATA.items():
        lines.append({
            "code": key,
            "name": data["name"],
            "color": data["color"],
            "first_train": data["first_train"],
            "last_train": data["last_train"],
            "total_stations": len(data["stations"])
        })
    return {"lines": lines}

@app.get("/stations/{line_code}")
def get_stations(line_code: str):
    if line_code not in METRO_DATA:
        raise HTTPException(status_code=404, detail="Line not found")

    line = METRO_DATA[line_code]
    return {
        "line": line["name"],
        "color": line["color"],
        "stations": line["stations"],
        "first_train": line["first_train"],
        "last_train": line["last_train"]
    }

@app.get("/station-info/{station_name}")
def get_station_info(station_name: str):
    if station_name not in STATION_FACILITIES:
        return {
            "station": station_name,
            "found": False,
            "message": "Detailed info not available for this station"
        }

    info = STATION_FACILITIES[station_name]
    return {
        "station": station_name,
        "found": True,
        "gates": info.get("gates", []),
        "landmarks": info.get("landmarks", ""),
        "lost_found": info.get("lost_found", False),
        "restrooms": info.get("restrooms", False),
        "parking": info.get("parking", False)
    }

@app.get("/emergency")
def get_emergency():
    return {
        "customer_care": "155370",
        "cisf_security": "155655",
        "lost_found": "Kashmere Gate Station",
        "women_safety": "155370",
        "medical": "155370"
    }

# ==================== FUZZY SEARCH ENDPOINTS ====================

@app.get("/api/fuzzy-search")
def fuzzy_search_endpoint(q: str, limit: int = 8, threshold: int = 60):
    """
    Search stations with fuzzy matching (typo-tolerant).
    Example: /api/fuzzy-search?q=rajeev+chok&limit=5
    """
    if not FUZZY_SEARCH_AVAILABLE or not STATION_LOADER:
        raise HTTPException(status_code=503, detail="Fuzzy search not available")
    
    if not q or len(q) < 1:
        return {"query": q, "results": [], "total": 0}
    
    station_names = list(STATION_LOADER.stations.keys())
    results = fuzzy_search_station(q, station_names, limit=limit, threshold=threshold)
    
    # Enhance results with station details
    enhanced = []
    for r in results:
        station = STATION_LOADER.get_station(r["name"])
        if station:
            enhanced.append({
                "name": r["name"],
                "score": round(r["score"], 2),
                "lines": station.get('lines', []),
                "is_interchange": len(station.get('lines', [])) > 1
            })
    
    return {
        "query": q,
        "results": enhanced,
        "total": len(enhanced),
        "threshold": threshold
    }


@app.get("/api/autocomplete")
def autocomplete_endpoint(q: str, limit: int = 5):
    """
    Autocomplete station names with fuzzy matching.
    Example: /api/autocomplete?q=khan&limit=5
    """
    if not FUZZY_SEARCH_AVAILABLE or not STATION_LOADER:
        raise HTTPException(status_code=503, detail="Autocomplete not available")
    
    if not q or len(q) < 1:
        return {"query": q, "suggestions": [], "total": 0}
    
    station_names = list(STATION_LOADER.stations.keys())
    suggestions = autocomplete_station(q, station_names, limit=limit)
    
    return {
        "query": q,
        "suggestions": suggestions,
        "total": len(suggestions)
    }


@app.get("/api/best-match")
def best_match_endpoint(q: str):
    """
    Find single best matching station.
    Example: /api/best-match?q=chandi+chawk
    """
    if not FUZZY_SEARCH_AVAILABLE or not STATION_LOADER:
        raise HTTPException(status_code=503, detail="Best match not available")
    
    if not q:
        raise HTTPException(status_code=400, detail="Query required")
    
    station_names = list(STATION_LOADER.stations.keys())
    best = best_match_station(q, station_names)
    
    if not best:
        raise HTTPException(status_code=404, detail="No matching station found")
    
    station = STATION_LOADER.get_station(best)
    
    return {
        "query": q,
        "best_match": best,
        "lines": station.get('lines', []),
        "is_interchange": len(station.get('lines', [])) > 1
    }

# ==================== STATION LOADER ENDPOINTS ====================

@app.get("/station/{station_name}")
def get_station(station_name: str):
    """
    Get comprehensive station information.
    Example: /station/Rajiv%20Chowk
    """
    if not STATION_LOADER:
        # Fallback for when CSV loader is not active
        canonical = normalize_station(station_name)
        if not canonical:
            raise HTTPException(status_code=404, detail="Station not found")
        
        lines = get_station_lines(canonical)
        return {
            "name": canonical,
            "lines": lines,
            "coordinates": {"lat": None, "lon": None},
            "is_interchange": len(lines) > 1,
            "lines_detail": {}
        }
    
    station = STATION_LOADER.get_station(station_name)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    
    response = {
        "name": station.get('name'),
        "lines": station.get('lines', []),
        "coordinates": station.get('coordinates', {}),
        "is_interchange": len(station.get('lines', [])) > 1,
        "lines_detail": {}
    }
    
    # Get neighbors on each line
    for line in station.get('lines', []):
        try:
            line_stations = STATION_LOADER.get_line_stations(line)
            if station.get('name') in line_stations:
                idx = line_stations.index(station['name'])
                response['lines_detail'][line] = {
                    "position_on_line": idx + 1,
                    "total_stations": len(line_stations),
                    "next_station": line_stations[idx + 1] if idx < len(line_stations) - 1 else None,
                    "prev_station": line_stations[idx - 1] if idx > 0 else None,
                }
        except:
            pass
    
    return response


@app.get("/api/lines")
def get_all_lines_enhanced():
    """
    Get list of all available metro lines with station counts.
    """
    if not STATION_LOADER:
        # Fallback to METRO_DATA if StationLoader is not available
        lines_info = []
        for key, data in METRO_DATA.items():
            lines_info.append({
                "name": key,
                "total_stations": len(data["stations"]),
                "start": data["stations"][0] if data["stations"] else None,
                "end": data["stations"][-1] if data["stations"] else None
            })
        return {"total_lines": len(lines_info), "lines": lines_info}
    
    lines_info = []
    for line in STATION_LOADER.list_all_lines():
        try:
            stations = STATION_LOADER.get_line_stations(line)
            lines_info.append({
                "name": line,
                "total_stations": len(stations),
                "start": stations[0] if stations else None,
                "end": stations[-1] if stations else None
            })
        except:
            pass
    
    return {
        "total_lines": len(lines_info),
        "lines": lines_info
    }

@app.get("/api/stations")
def get_all_stations_list():
    """Get a flat list of all station names for dropdowns."""
    if STATION_LOADER:
        # Return stations from CSV if available
        return {"stations": sorted([s["name"] for s in STATION_LOADER.stations.values()])}
    
    # Fallback to METRO_DATA
    all_stations = set()
    for line in METRO_DATA.values():
        for s in line["stations"]:
            all_stations.add(s)
    return {"stations": sorted(list(all_stations))}

@app.get("/dashboard")
def dashboard_ui():
    return FileResponse("dashboard.html")

@app.get("/api/nearest")
def get_nearest_station(lat: float, lon: float, limit: int = 3):
    """
    Find nearest metro stations to given coordinates.
    Example: /api/nearest?lat=28.6328&lon=77.2197
    """
    if not STATION_LOADER:
        raise HTTPException(status_code=503, detail="Station data not available")
    
    results = STATION_LOADER.nearby(lat, lon, radius_km=10.0)
    
    return {
        "count": len(results[:limit]),
        "stations": [
            {"name": s["name"], "distance_km": round(d, 2), "lines": s["lines"]}
            for d, s in results[:limit]
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
