from flask import Flask, render_template, request, jsonify
import sys
import os
import re
import webbrowser
from threading import Timer

# Ensure we can import from the current directory
sys.path.append(os.getcwd())

# Import the logic we built in Parts 1-3 (Combined in dmrc_complete.py)
try:
    from dmrc_complete import find_route, validate_station, format_route_text
except ImportError:
    print("❌ Error: 'dmrc_complete.py' not found. Please ensure Part 1-5 are combined.")
    sys.exit(1)

app = Flask(__name__, static_folder='static', template_folder='templates')

# ==========================================
# PART 5: FLASK BACKEND API
# ==========================================

@app.route('/')
def index():
    """
    Redirect root to dashboard.
    This helps relative paths in HTML (like ../static) work correctly.
    """
    return '<script>window.location.href="/dashboard";</script>'

@app.route('/dashboard')
def dashboard():
    """
    Serve the HTML Dashboard.
    """
    return render_template('dashboard.html')

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """
    Handle Chat & Route Requests.
    Expected JSON: { "message": "Rajiv Chowk to Noida" }
    """
    data = request.json
    if not data or 'message' not in data:
        return jsonify({"response": "⚠️ Error: No message received."}), 400

    user_msg = data['message'].strip()
    response_text = ""
    route_info = None
    
    # --- Intent Recognition ---
    lower_msg = user_msg.lower()

    # 1. Route Query (Heuristic: contains " to ")
    # We use regex to split case-insensitively on " to "
    parts = re.split(r'\s+to\s+', user_msg, flags=re.IGNORECASE)
    
    if len(parts) >= 2 and " to " in lower_msg:
        # Assume format: "Origin to Destination"
        src_raw = parts[0].strip()
        dst_raw = parts[1].strip()
        
        # Validate Stations
        valid_src, src_name = validate_station(src_raw)
        valid_dst, dst_name = validate_station(dst_raw)
        
        if valid_src and valid_dst:
            # Calculate Route
            route_data = find_route(src_name, dst_name)
            
            if "error" in route_data:
                response_text = f"⚠️ {route_data['error']}"
            else:
                # Success: Get formatted text AND raw data for UI
                response_text = format_route_text(route_data)
                route_info = route_data
        else:
            # Handle Typo/Unknown Stations
            suggestions = []
            if not valid_src:
                msg = f"❌ Station **'{src_raw}'** not found."
                if src_name: msg += f" Did you mean **{src_name}**?"
                suggestions.append(msg)
            if not valid_dst:
                msg = f"❌ Station **'{dst_raw}'** not found."
                if dst_name: msg += f" Did you mean **{dst_name}**?"
                suggestions.append(msg)
            
            response_text = "\n".join(suggestions)

    # 2. Map Request
    elif "map" in lower_msg:
        response_text = "🗺️ **Network Map**\nI've opened the map view in the side panel."
        # In a real app, we'd send a flag to switch UI tabs
        
    # 3. Fare Request
    elif "fare" in lower_msg:
        response_text = "💰 **Fare Calculator**\nPlease enter a route (e.g., *'Hauz Khas to Saket'*) to see the fare."

    # 4. Greetings
    elif any(w in lower_msg for w in ['hi', 'hello', 'hey', 'start']):
        response_text = (
            "👋 **Hello! I'm MetroSahayak.**\n"
            "I can help you find the fastest metro routes.\n\n"
            "Try asking:\n"
            "• *Rajiv Chowk to Noida City Centre*\n"
            "• *Kashmere Gate to Huda City Centre*"
        )

    # 5. Fallback
    else:
        response_text = (
            "🤔 I didn't catch that.\n"
            "Please ask for a route like: **'Station A to Station B'**"
        )

    return jsonify({
        "response": response_text,
        "route_info": route_info
    })

if __name__ == '__main__':
    print("\n=================================================")
    print("  🚇 MetroSahayak Backend Running")
    print("  👉 Open: http://localhost:5000/dashboard")
    print("=================================================\n")

    def open_browser():
        webbrowser.open_new("http://localhost:5000/dashboard")

    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        Timer(1.5, open_browser).start()

    app.run(host='0.0.0.0', port=5000, debug=True)