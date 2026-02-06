import React, { useState, useRef, useEffect } from 'react';
import { Send, MessageCircle, Map, AlertCircle, Clock, CreditCard, MapPin, Info } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import './App.css';

const API_BASE_URL = 'http://localhost:8000';

// Enhanced Language Strings
const STRINGS = {
  en: {
    title: "MetroSahayak",
    subtitle: "Your Delhi Metro Assistant",
    placeholder: "Ask about routes, fares, timings, or emergency help...",
    sendBtn: "Send",
    chat: "Chat",
    route: "Find Route",
    info: "Info",
    emergency: "Emergency",
    fromStation: "From Station",
    toStation: "To Station",
    search: "Search Route",
    selectStation: "Select a station...",
    quickActions: {
      timings: "Metro Timings",
      recharge: "Card Recharge",
      lines: "Metro Lines",
      peak: "Peak Hours"
    }
  },
  hi: {
    title: "मेट्रो साहायक",
    subtitle: "आपका दिल्ली मेट्रो सहायक",
    placeholder: "रूट, किराया, समय के बारे में पूछें...",
    sendBtn: "भेजें",
    chat: "चैट",
    route: "रूट खोजें",
    info: "जानकारी",
    emergency: "आपातकाल",
    fromStation: "कहाँ से",
    toStation: "कहाँ तक",
    search: "रूट खोजें",
    selectStation: "एक स्टेशन चुनें...",
    quickActions: {
      timings: "मेट्रो समय",
      recharge: "कार्ड रिचार्ज",
      lines: "मेट्रो लाइनें",
      peak: "पीक आवर्स"
    }
  }
};

// Enhanced Knowledge Base
const CHATBOT_KNOWLEDGE = {
  timings: {
    keywords: ['timing', 'time', 'open', 'close', 'schedule', 'hours', 'समय'],
    response: `🕐 Delhi Metro Operating Hours:

Monday to Saturday: 6:00 AM - 11:00 PM
Sunday: 6:00 AM - 10:00 PM

First Train: Around 5:00 AM - 6:00 AM (varies by line)
Last Train: Around 10:30 PM - 11:30 PM (varies by line)

Note: Timings may vary on special occasions and public holidays.`
  },
  recharge: {
    keywords: ['recharge', 'topup', 'top-up', 'reload', 'card', 'रिचार्ज'],
    response: `💳 Metro Card Recharge Methods:

1. At Metro Stations:
   - AFC (Automatic Fare Collection) counters
   - TVM (Ticket Vending Machines)
   - Recharge kiosks

2. Online Methods:
   - Delhi Metro Rail App (DMRC)
   - Paytm, PhonePe, Google Pay
   - Official DMRC website

3. Mobile Wallets:
   - Link your metro card
   - Auto-recharge options available

Minimum recharge: ₹100
Maximum balance: ₹3000`
  },
  lines: {
    keywords: ['line', 'lines', 'color', 'route map', 'लाइन'],
    response: `🗺️ Delhi Metro Lines:

🔴 Red Line: Rithala - Shaheed Sthal (New Bus Adda)
🔵 Blue Line: Dwarka Sector 21 - Noida Electronic City/Vaishali
🟡 Yellow Line: Samaypur Badli - HUDA City Centre
🟢 Green Line: Brigadier Hoshiar Singh - Kirti Nagar
🟣 Violet Line: Kashmere Gate - Raja Nahar Singh (Ballabhgarh)
🟠 Orange Line: AIIMS - New Delhi (Airport Express)
🩷 Pink Line: Majlis Park - Shiv Vihar
🩶 Grey Line: Dwarka - Najafgarh
⚪ Rapid Metro: Sikanderpur - Cyber City

Total: 350+ stations across 390+ km`
  },
  peak: {
    keywords: ['peak', 'rush', 'busy', 'crowd', 'पीक'],
    response: `📊 Peak Hours & Off-Peak Timings:

Morning Peak Hours:
🔺 8:00 AM - 10:00 AM

Evening Peak Hours:
🔺 5:00 PM - 8:00 PM

Off-Peak Hours:
✅ 10:00 AM - 5:00 PM
✅ After 8:00 PM

💡 Tip: Travel during off-peak hours for:
- Less crowded trains
- Discounted fares (10% off on smart cards)
- More comfortable journey`
  },
  fare: {
    keywords: ['fare', 'price', 'cost', 'ticket', 'charge', 'किराया'],
    response: `💰 Delhi Metro Fare Structure:

Distance-based fares:
📍 0-2 km: ₹10
📍 2-5 km: ₹20
📍 5-12 km: ₹30
📍 12-21 km: ₹40
📍 21-32 km: ₹50
📍 32+ km: ₹60

Airport Express Line:
✈️ ₹60 (New Delhi to Airport)

Smart Card Benefits:
💳 10% discount on every journey
💳 Faster entry/exit
💳 No need to buy tokens`
  },
  airport: {
    keywords: ['airport', 'flight', 'terminal', 'igi', 'एयरपोर्ट'],
    response: `✈️ Delhi Airport Metro Connection:

Orange Line (Airport Express):
🔸 New Delhi → IGI Airport T3
🔸 Stations: New Delhi, Shivaji Stadium, Dhaula Kuan, Airport (T3)

Travel Time: ~20 minutes
Frequency: Every 10-15 minutes
Fare: ₹60

💡 Tip: Airport Express is fastest! Luggage space available.`
  },
  wifi: {
    keywords: ['wifi', 'internet', 'connectivity', 'data'],
    response: `📶 Delhi Metro WiFi:

Free WiFi Available at:
✅ All underground stations
✅ Major interchange stations

How to Connect:
1. Search for "DelhiMetro-Wifi"
2. Accept terms & conditions
3. Enter mobile number
4. Receive OTP & login

💡 Tip: Download content before boarding!`
  },
  parking: {
    keywords: ['parking', 'park', 'vehicle', 'car'],
    response: `🅿️ Metro Station Parking:

Available at major stations:
- Noida Sector 16
- Dwarka Sector 21
- Kashmere Gate
- Rajiv Chowk

Charges (approx):
🚗 Cars: ₹40 for first 4 hours
🏍️ Two-wheelers: ₹20 for first 4 hours

💡 Tip: Use Park & Ride to avoid traffic!`
  },
  facilities: {
    keywords: ['facilities', 'amenities', 'washroom', 'atm', 'सुविधा'],
    response: `🏢 Metro Station Facilities:

Available at Most Stations:
✅ Clean Washrooms (paid)
✅ ATMs
✅ Drinking Water
✅ First Aid
✅ Elevators & Escalators
✅ Help Desks

Special Facilities:
♿ Wheelchair assistance
👶 Baby care rooms (select stations)
🛒 Retail shops
☕ Cafes (major stations)`
  },
  rules: {
    keywords: ['rule', 'rules', 'allowed', 'prohibited', 'banned', 'नियम'],
    response: `⚠️ Metro Rules & Regulations:

❌ PROHIBITED:
- Smoking, eating, drinking
- Carrying flammable items
- Pets (except guide dogs)
- Playing music without earphones

✅ ALLOWED:
- 2 pieces of luggage (max 25kg each)
- Laptops, electronics
- Folded bicycles (designated coaches)

⚖️ Penalties: Fine up to ₹500`
  },
  lost: {
    keywords: ['lost', 'found', 'missing', 'forgot', 'खोया'],
    response: `📦 Lost & Found:

Main Office:
📍 Kashmere Gate Metro Station
📞 011-23417910
⏰ 8:00 AM - 8:00 PM (Mon-Sat)

What to do:
1. Report to station manager immediately
2. File written complaint
3. Provide item description
4. Keep contact info updated`
  }
};

// Animated Metro Logo Component
const AnimatedMetroLogo = () => (
  <motion.div
    className="animated-logo"
    animate={{
      x: [0, 10, 0],
      y: [0, -5, 0]
    }}
    transition={{
      duration: 3,
      repeat: Infinity,
      ease: "easeInOut"
    }}
  >
    <svg width="60" height="45" viewBox="0 0 80 60" xmlns="http://www.w3.org/2000/svg">
      {/* Train Body */}
      <motion.rect
        className="train-body"
        x="10" y="15" width="60" height="30" rx="5"
        fill="white"
        animate={{ scale: [1, 1.02, 1] }}
        transition={{ duration: 2, repeat: Infinity }}
      />
      
      {/* Windows */}
      <motion.rect
        x="20" y="20" width="10" height="12" rx="2"
        fill="#02555B"
        animate={{ opacity: [0.7, 1, 0.7] }}
        transition={{ duration: 1.5, repeat: Infinity }}
      />
      <rect x="35" y="20" width="10" height="12" rx="2" fill="#02555B"/>
      <rect x="50" y="20" width="10" height="12" rx="2" fill="#02555B"/>
      
      {/* Wheels */}
      <motion.circle
        cx="25" cy="45" r="5"
        fill="#FFCE00"
        animate={{ rotate: 360 }}
        transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
      />
      <motion.circle
        cx="55" cy="45" r="5"
        fill="#FFCE00"
        animate={{ rotate: 360 }}
        transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
      />
      
      {/* Front Light */}
      <motion.circle
        cx="8" cy="30" r="3"
        fill="#FFCE00"
        animate={{ opacity: [1, 0.5, 1] }}
        transition={{ duration: 1, repeat: Infinity }}
      />
    </svg>
  </motion.div>
);

// 3D Mascot Component
const Mascot3D = () => (
  <motion.div
    className="mascot-3d"
    animate={{
      y: [0, -15, 0],
      rotate: [0, 5, 0, -5, 0]
    }}
    transition={{
      duration: 4,
      repeat: Infinity,
      ease: "easeInOut"
    }}
  >
    <motion.div
      className="mascot-sphere"
      whileHover={{ scale: 1.1, rotateY: 180 }}
      transition={{ duration: 0.5 }}
    >
      🚇
    </motion.div>
  </motion.div>
);

// Quick Action Button Component
const QuickActionButton = ({ icon, text, onClick }) => (
  <motion.button
    className="quick-action-btn"
    onClick={onClick}
    whileHover={{ scale: 1.05, y: -5 }}
    whileTap={{ scale: 0.95 }}
  >
    <div className="quick-action-icon">{icon}</div>
    <div className="quick-action-text">{text}</div>
  </motion.button>
);

// Chat Message Component with Animation
const ChatMessage = ({ message, isUser }) => (
  <motion.div
    initial={{ opacity: 0, y: 20, scale: 0.8 }}
    animate={{ opacity: 1, y: 0, scale: 1 }}
    transition={{ duration: 0.4, type: "spring" }}
    className={`chat-message ${isUser ? 'user' : 'bot'}`}
  >
    <div className={`message-content ${isUser ? 'user-content' : 'bot-content'}`}>
      {message.split('\n').map((line, i) => (
        <React.Fragment key={i}>
          {line}
          {i < message.split('\n').length - 1 && <br />}
        </React.Fragment>
      ))}
    </div>
  </motion.div>
);

// Route Display Component
const RouteDisplay = ({ route, language }) => (
  <motion.div
    initial={{ opacity: 0, scale: 0.9 }}
    animate={{ opacity: 1, scale: 1 }}
    className="route-display-3d"
  >
    <h3 className="route-title">✅ Route Found!</h3>

    <div className="route-info-card">
      <p><strong>From:</strong> {route.from_station}</p>
      <p><strong>To:</strong> {route.to_station}</p>
      <p><strong>Distance:</strong> {route.distance} stations</p>
    </div>

    <div className="stations-list-3d">
      <h4>🚇 Journey Path</h4>
      {route.stations.map((station, index) => (
        <motion.div
          key={index}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: index * 0.05 }}
          className="station-item-3d"
        >
          <span className="station-number-3d">{index + 1}</span>
          <span className="station-name-3d">{station}</span>
        </motion.div>
      ))}
    </div>

    {route.interchanges.length > 0 && (
      <div className="interchanges-3d">
        <h4>🔄 Interchange Stations</h4>
        {route.interchanges.map((interchange, index) => (
          <div key={index} className="interchange-item-3d">
            <strong>{interchange.station}</strong>
            <span className="lines-badge">{interchange.lines.join(' ↔ ')}</span>
          </div>
        ))}
      </div>
    )}

    <div className="fare-info-3d">
      <h4>💰 Fare Details</h4>
      <div className="fare-row">
        <span>Token Fare:</span>
        <span className="fare-amount">₹{route.fare.base_fare}</span>
      </div>
      <div className="fare-row">
        <span>Off-Peak:</span>
        <span className="fare-amount">₹{route.fare.off_peak_fare}</span>
      </div>
      <div className="fare-row">
        <span>Smart Card:</span>
        <span className="fare-amount">₹{route.fare.smart_card_fare}</span>
      </div>
    </div>
  </motion.div>
);

// Main App Component
export default function MetroSahayak() {
  const [messages, setMessages] = useState([
    {
      text: "👋 Welcome to MetroSahayak! I'm your Delhi Metro assistant. Ask me about:\n\n🚇 Routes & Stations\n💰 Fares & Cards\n⏰ Timings & Schedules\n🗺️ Metro Lines\n🚨 Emergency Help\n\nHow can I help you today?",
      isUser: false
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [language, setLanguage] = useState('en');
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('chat');
  const [fromStation, setFromStation] = useState('');
  const [toStation, setToStation] = useState('');
  const [stations, setStations] = useState([]);
  const messagesEndRef = useRef(null);

  const strings = STRINGS[language];

  useEffect(() => {
    fetchAllStations();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchAllStations = async () => {
    try {
      const linesResp = await axios.get(`${API_BASE_URL}/lines`);
      const lineCodes = linesResp.data.lines.map(l => l.code);

      const responses = await Promise.all(
        lineCodes.map(code => axios.get(`${API_BASE_URL}/stations/${code}`))
      );

      const allStations = [];
      const stationSet = new Set();

      responses.forEach(response => {
        response.data.stations.forEach(station => {
          if (!stationSet.has(station)) {
            allStations.push(station);
            stationSet.add(station);
          }
        });
      });

      setStations(allStations.sort((a, b) => a.localeCompare(b)));
    } catch (error) {
      console.error('Error fetching stations:', error);
    }
  };

  const getLocalResponse = (message) => {
    const lowerMessage = message.toLowerCase();
    
    for (const [key, data] of Object.entries(CHATBOT_KNOWLEDGE)) {
      if (data.keywords.some(keyword => lowerMessage.includes(keyword))) {
        return data.response;
      }
    }
    
    return null;
  };

  const handleSendMessage = async (messageText = null) => {
    const userMessage = messageText || inputValue.trim();
    if (!userMessage) return;

    setMessages(prev => [...prev, { text: userMessage, isUser: true }]);
    setInputValue('');
    setLoading(true);

    // Check local knowledge first
    const localResponse = getLocalResponse(userMessage);
    
    setTimeout(async () => {
      if (localResponse) {
        setMessages(prev => [...prev, { text: localResponse, isUser: false }]);
        setLoading(false);
      } else {
        // Try API
        try {
          const response = await axios.post(`${API_BASE_URL}/chat`, {
            message: userMessage,
            language: language
          });
          setMessages(prev => [...prev, { text: response.data.response, isUser: false }]);
        } catch (error) {
          setMessages(prev => [...prev, {
            text: "I can help you with metro routes, timings, fares, and more! Try asking about specific topics.",
            isUser: false
          }]);
        }
        setLoading(false);
      }
    }, 800);
  };

  const handleFindRoute = async () => {
    if (!fromStation || !toStation) {
      setMessages(prev => [...prev, {
        text: "❌ Please select both stations",
        isUser: false,
        type: 'error'
      }]);
      return;
    }

    setLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/route`, {
        from_station: fromStation,
        to_station: toStation,
        language: language
      });

      setMessages(prev => [...prev, {
        type: 'route',
        data: response.data,
        isUser: false
      }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        text: `❌ ${error.response?.data?.detail || 'Error finding route'}`,
        isUser: false
      }]);
    }

    setLoading(false);
  };

  return (
    <div className="metro-app-3d">
      {/* Mascot */}
      <Mascot3D />

      {/* Header */}
      <motion.div
        className="header-3d"
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ type: "spring", stiffness: 100 }}
      >
        <div className="header-content">
          <AnimatedMetroLogo />
          <div className="header-text">
            <h1>{strings.title}</h1>
            <p>🇮🇳 {strings.subtitle}</p>
          </div>
        </div>
      </motion.div>

      {/* Tab Navigation */}
      <div className="tab-navigation-3d">
        <motion.button
          className={`tab-btn-3d ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => setActiveTab('chat')}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <MessageCircle size={20} />
          <span>{strings.chat}</span>
        </motion.button>

        <motion.button
          className={`tab-btn-3d ${activeTab === 'route' ? 'active' : ''}`}
          onClick={() => setActiveTab('route')}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Map size={20} />
          <span>{strings.route}</span>
        </motion.button>

        <motion.button
          className={`tab-btn-3d ${activeTab === 'emergency' ? 'active' : ''}`}
          onClick={() => setActiveTab('emergency')}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <AlertCircle size={20} />
          <span>{strings.emergency}</span>
        </motion.button>
      </div>

      {/* Chat Tab */}
      {activeTab === 'chat' && (
        <div className="chat-container-3d">
          {/* Quick Actions */}
          <div className="quick-actions-grid">
            <QuickActionButton
              icon="⏰"
              text={strings.quickActions.timings}
              onClick={() => handleSendMessage("What are the metro timings?")}
            />
            <QuickActionButton
              icon="💳"
              text={strings.quickActions.recharge}
              onClick={() => handleSendMessage("How to recharge metro card?")}
            />
            <QuickActionButton
              icon="🗺️"
              text={strings.quickActions.lines}
              onClick={() => handleSendMessage("Show me all metro lines")}
            />
            <QuickActionButton
              icon="📊"
              text={strings.quickActions.peak}
              onClick={() => handleSendMessage("What are the peak hours?")}
            />
          </div>

          <div className="messages-container-3d">
            <AnimatePresence>
              {messages.map((msg, index) => (
                msg.type === 'route' ? (
                  <div key={index}>
                    <RouteDisplay route={msg.data} language={language} />
                  </div>
                ) : (
                  <ChatMessage
                    key={index}
                    message={msg.text}
                    isUser={msg.isUser}
                  />
                )
              ))}
            </AnimatePresence>
            {loading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="loading-indicator-3d"
              >
                <span></span><span></span><span></span>
              </motion.div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={(e) => { e.preventDefault(); handleSendMessage(); }} className="input-form-3d">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder={strings.placeholder}
              className="chat-input-3d"
              disabled={loading}
            />
            <motion.button
              type="submit"
              disabled={loading}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="send-btn-3d"
            >
              <Send size={20} />
            </motion.button>
          </form>
        </div>
      )}

      {/* Route Tab */}
      {activeTab === 'route' && (
        <div className="route-container-3d">
          <div className="route-form-3d">
            <div className="form-group-3d">
              <label>📍 {strings.fromStation}</label>
              <select
                value={fromStation}
                onChange={(e) => setFromStation(e.target.value)}
                className="station-select-3d"
              >
                <option value="">{strings.selectStation}</option>
                {stations.map((station, index) => (
                  <option key={index} value={station}>{station}</option>
                ))}
              </select>
            </div>

            <div className="form-group-3d">
              <label>🎯 {strings.toStation}</label>
              <select
                value={toStation}
                onChange={(e) => setToStation(e.target.value)}
                className="station-select-3d"
              >
                <option value="">{strings.selectStation}</option>
                {stations.map((station, index) => (
                  <option key={index} value={station}>{station}</option>
                ))}
              </select>
            </div>

            <motion.button
              onClick={handleFindRoute}
              disabled={loading}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="search-btn-3d"
            >
              🔍 {strings.search}
            </motion.button>
          </div>

          <div className="route-messages-3d">
            <AnimatePresence>
              {messages
                .filter(msg => msg.type === 'route' || msg.type === 'error')
                .map((msg, index) => (
                  msg.type === 'route' ? (
                    <div key={index}>
                      <RouteDisplay route={msg.data} language={language} />
                    </div>
                  ) : (
                    <ChatMessage key={index} message={msg.text} isUser={false} />
                  )
                ))}
            </AnimatePresence>
          </div>
        </div>
      )}

      {/* Emergency Tab */}
      {activeTab === 'emergency' && (
        <motion.div
          className="emergency-container-3d"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <div className="emergency-grid-3d">
            {[
              { title: '📞 Customer Care', number: '155370' },
              { title: '🛡️ Security (CISF)', number: '155655' },
              { title: '📦 Lost & Found', number: 'Kashmere Gate' },
              { title: '🏥 Medical', number: '155370' },
              { title: '👩 Women Safety', number: '155370' },
              { title: '🚨 Police', number: '100' }
            ].map((contact, index) => (
              <motion.div
                key={index}
                className="contact-card-3d"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ scale: 1.05, y: -5 }}
              >
                <h3>{contact.title}</h3>
                <p>{contact.number}</p>
              </motion.div>
            ))}
          </div>

          <motion.div
            className="emergency-tips-3d"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
          >
            <h3>🛡️ Safety Tips</h3>
            <ul>
              <li>Keep your belongings safe and secure</li>
              <li>Use designated women's coaches during peak hours</li>
              <li>Report suspicious activity immediately</li>
              <li>Keep emergency contacts saved</li>
              <li>Stand behind the yellow line on platforms</li>
              <li>Avoid traveling alone late at night</li>
            </ul>
          </motion.div>
        </motion.div>
      )}
    </div>
  );
}
