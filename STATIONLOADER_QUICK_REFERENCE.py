"""
STATIONLOADER - QUICK REFERENCE CARD
====================================
Quick copy-paste solutions for common tasks
"""

# ============================================================================
# 1. BASIC INITIALIZATION
# ============================================================================

from station_loader import StationLoader

loader = StationLoader("dmrc_stations_dataset.csv")
# All data loaded!


# ============================================================================
# 2. GET STATION INFO
# ============================================================================

station = loader.get_station("Connaught Place")
print(station['name'])          # "Connaught Place"
print(station['lines'])         # ['blue', 'yellow']
print(len(station['lines']) > 1) # True = interchange


# ============================================================================
# 3. SEARCH FOR STATIONS
# ============================================================================

# Search for stations containing a word
results = loader.search("khan")
for s in results:
    print(s['name'])  # Khan Market, Khanpur

# Check specific station exists
if loader.get_station("Terminal 1 IGI Airport"):
    print("Found!")


# ============================================================================
# 4. LIST STATIONS ON A LINE
# ============================================================================

blue_stations = loader.get_line_stations("blue")
print(f"Blue line: {len(blue_stations)} stations")
print(f"Start: {blue_stations[0]}")
print(f"End: {blue_stations[-1]}")
print(f"All: {' -> '.join(blue_stations)}")


# ============================================================================
# 5. GET ALL LINES
# ============================================================================

lines = loader.list_all_lines()
for line in lines:
    stations = loader.get_line_stations(line)
    print(f"{line}: {len(stations)} stations")


# ============================================================================
# 6. FIND INTERCHANGE STATIONS
# ============================================================================

# All interchanges
interchanges = [s for s in loader.stations.values() if len(s['lines']) > 1]
print(f"Total: {len(interchanges)} interchange stations")

# Top 5 busiest
top = sorted(interchanges, key=lambda x: len(x['lines']), reverse=True)[:5]
for s in top:
    print(f"{s['name']}: {len(s['lines'])} lines")


# ============================================================================
# 7. CHECK IF TWO STATIONS ON SAME LINE
# ============================================================================

station_a = loader.get_station("Rajiv Chowk")
station_b = loader.get_station("Connaught Place")

common_lines = set(station_a['lines']) & set(station_b['lines'])
if common_lines:
    print(f"Direct route via {list(common_lines)[0]} line")
else:
    print("Need to interchange")


# ============================================================================
# 8. FIND INTERCHANGE POINT FOR TWO STATIONS
# ============================================================================

def find_interchange(station_a, station_b):
    a = loader.get_station(station_a)
    b = loader.get_station(station_b)
    a_lines = set(a['lines'])
    b_lines = set(b['lines'])
    
    # Check direct connection
    if a_lines & b_lines:
        return f"Direct via {list(a_lines & b_lines)[0]} line"
    
    # Find interchange stations
    for s in loader.stations.values():
        s_lines = set(s['lines'])
        if (s_lines & a_lines) and (s_lines & b_lines):
            return f"Interchange at {s['name']}"
    
    return "No connection found"

print(find_interchange("Rajiv Chowk", "New Delhi"))


# ============================================================================
# 9. GET STATION DETAILS
# ============================================================================

station = loader.get_station("New Delhi")
if station:
    info = {
        "name": station['name'],
        "lines": station['lines'],
        "num_lines": len(station['lines']),
        "is_interchange": len(station['lines']) > 1,
        "longitude": station['coordinates']['lon'],
        "latitude": station['coordinates']['lat'],
    }
    print(info)


# ============================================================================
# 10. GET NEIGHBORS (ADJACENT STATIONS)
# ============================================================================

neighbors = loader.get_neighbors("Central Secretariat")
for neighbor, distance in neighbors.items():
    print(f"{neighbor}: {distance:.2f}km")


# ============================================================================
# 11. ITERATE ALL STATIONS
# ============================================================================

for name, station in loader.stations.items():
    print(f"{name} ({', '.join(station['lines'])})")


# ============================================================================
# 12. FASTAPI ENDPOINT EXAMPLES (Reference Only - Not Executed)
# ============================================================================
"""
These are example FastAPI endpoints - uncomment to use in a separate app.py file

from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/station/{name}")
def get_station_endpoint(name: str):
    s = loader.get_station(name)
    if not s:
        raise HTTPException(status_code=404)
    return {"name": s['name'], "lines": s['lines'], "interchange": len(s['lines']) > 1}

@app.get("/line/{line}")
def get_line_endpoint(line: str):
    stations = loader.get_line_stations(line)
    if not stations:
        raise HTTPException(status_code=404)
    return {"line": line, "stations": stations, "total": len(stations)}

@app.get("/search/")
def search_endpoint(q: str):
    results = loader.search(q)
    return {"query": q, "results": [s['name'] for s in results]}
"""


# ============================================================================
# 13. CHATBOT INTENT HANDLING
# ============================================================================

def extract_station(user_input):
    """Extract station name from user input - improved version"""
    # Look for exact station names first
    user_lower = user_input.lower()
    
    # Try exact matches first (case-insensitive)
    for name in loader.stations.keys():
        if name.lower() in user_lower:
            return name
    
    # Try searching for keywords
    words = user_lower.split()
    for word in words:
        results = loader.search(word)
        if results:
            return results[0]['name']
    
    return None


def extract_line(user_input):
    """Extract line name from user input"""
    lines = ['red', 'yellow', 'blue', 'green', 'violet', 'pink', 'magenta', 'grey', 'airport']
    user_lower = user_input.lower()
    for line in lines:
        if line in user_lower:
            return line
    return None


def handle_station_query(user_input):
    """Route queries to appropriate handler"""
    
    # Query type 1: "Is X an interchange?"
    if "interchange" in user_input.lower():
        station_name = extract_station(user_input)
        if station_name:
            s = loader.get_station(station_name)
            if s and len(s['lines']) > 1:
                return f"Yes, {station_name} is an interchange between {' and '.join(s['lines'])} lines"
            else:
                return f"No, {station_name} is not an interchange"
        return "Could not identify station"
    
    # Query type 2: "Stations on X line"
    elif "line" in user_input.lower():
        line = extract_line(user_input)
        if line:
            stations = loader.get_line_stations(line)
            return f"{line.upper()} line has {len(stations)} stations: {' → '.join(stations[:5])}..."
        return "Could not identify line"
    
    # Query type 3: General station info
    else:
        station_name = extract_station(user_input)
        if station_name:
            s = loader.get_station(station_name)
            if s:
                return f"{s['name']} is on: {', '.join(s['lines'])}"
        return "I couldn't understand your query"


# ============================================================================
# 14. ERROR HANDLING
# ============================================================================

def safe_get_station(name):
    try:
        station = loader.get_station(name)
        if station:
            return station
        else:
            # Try fuzzy search
            results = loader.search(name)
            if results:
                print(f"Did you mean: {results[0]['name']}?")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None


# ============================================================================
# 15. TESTING & COMPREHENSIVE EXAMPLES
# ============================================================================

def test_station_loader():
    """Quick validation test"""
    
    tests = [
        ("Connaught Place found", loader.get_station("Connaught Place") is not None),
        ("Blue line has stations", len(loader.get_line_stations("blue")) > 0),
        ("Search works", len(loader.search("delhi")) > 0),
        ("Lines indexed", len(loader.list_all_lines()) > 0),
    ]
    
    for test_name, result in tests:
        status = "PASS" if result else "FAIL"
        print(f"[{status}] {test_name}")
    
    return all(r for _, r in tests)


def test_chatbot_functions():
    """Test chatbot query handling"""
    print("\n" + "="*70)
    print("CHATBOT QUERY TESTS")
    print("="*70)
    
    test_queries = [
        "Is Rajiv Chowk an interchange?",
        "What stations are on the blue line?",
        "Tell me about Connaught Place",
    ]
    
    for query in test_queries:
        result = handle_station_query(query)
        print(f"\n[QUERY] {query}")
        print(f"[RESPONSE] {result}")


def test_route_finding():
    """Test route finding functions"""
    print("\n" + "="*70)
    print("ROUTE FINDING TESTS")
    print("="*70)
    
    test_routes = [
        ("Rajiv Chowk", "New Delhi"),
        ("Khan Market", "Connaught Place"),
        ("Central Secretariat", "Rajiv Chowk"),
    ]
    
    for start, end in test_routes:
        result = find_interchange(start, end)
        print(f"\n[ROUTE] {start} -> {end}")
        print(f"        Result: {result}")


def test_neighbors():
    """Test neighbor finding"""
    print("\n" + "="*70)
    print("NEIGHBOR STATION TESTS")
    print("="*70)
    
    test_stations = ["Rajiv Chowk", "Khan Market", "New Delhi"]
    
    for station in test_stations:
        neighbors = loader.get_neighbors(station)
        if neighbors:
            print(f"\n[NEIGHBORS] {station}:")
            for neighbor, dist in list(neighbors.items())[:3]:  # Show first 3
                print(f"  - {neighbor}: {dist:.2f}km")
        else:
            print(f"\n[NEIGHBORS] {station}: No neighbor data available")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("STATIONLOADER - COMPREHENSIVE TEST SUITE")
    print("="*70)
    
    # Test 1: Basic loader tests
    print("\n[TESTS] BASIC LOADER TESTS")
    print("="*70)
    all_pass = test_station_loader()
    
    # Test 2: Chatbot functions
    test_chatbot_functions()
    
    # Test 3: Route finding
    test_route_finding()
    
    # Test 4: Neighbor analysis
    test_neighbors()
    
    # Final summary
    print("\n" + "="*70)
    print("ALL TESTS COMPLETE")
    print("="*70)
    if all_pass:
        print("[SUCCESS] All core tests passed!")
    else:
        print("[WARNING] Some tests failed - check output above")
    
    print(f"\n[SUMMARY] Metro Data Statistics:")
    print(f"  - Total stations: {len(loader.stations)}")
    print(f"  - Total lines: {len(loader.list_all_lines())}")
    interchanges = [s for s in loader.stations.values() if len(s['lines']) > 1]
    print(f"  - Interchange stations: {len(interchanges)}")
    print("="*70)
