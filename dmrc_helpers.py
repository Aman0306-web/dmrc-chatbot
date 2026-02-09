import difflib
from dmrc_graph import METRO_GRAPH

# ==========================================
# PART 4: HELPER FUNCTIONS & VALIDATION
# ==========================================

def normalize_station_name(name):
    """
    Cleans up user input: removes extra spaces, converts to Title Case.
    Example: "  rajiv   chowk " -> "Rajiv Chowk"
    """
    if not isinstance(name, str):
        return ""
    return " ".join(name.strip().split()).title()

def validate_station(name):
    """
    Validates if a station exists in the graph.
    Supports case-insensitive matching and fuzzy matching for typos.
    
    Returns:
        (True, Correct Station Name) if found
        (False, Suggestion) if close match found
        (False, None) if no match found
    """
    if not name:
        return False, None
        
    clean_name = normalize_station_name(name)
    
    # 1. Exact Match Check
    if clean_name in METRO_GRAPH:
        return True, clean_name
        
    # 2. Case-Insensitive Check
    stations_lower = {k.lower(): k for k in METRO_GRAPH.keys()}
    if clean_name.lower() in stations_lower:
        return True, stations_lower[clean_name.lower()]
        
    # 3. Fuzzy Match (Did you mean?)
    # Uses difflib to find names with >60% similarity
    matches = difflib.get_close_matches(clean_name, METRO_GRAPH.keys(), n=1, cutoff=0.6)
    if matches:
        return False, matches[0] # Return the suggestion
        
    return False, None

def format_route_text(route_result):
    """
    Formats the route dictionary from dmrc_routing.py into a user-friendly string.
    """
    if "error" in route_result:
        return f"⚠️ {route_result['error']}"
        
    src = route_result['source']
    dst = route_result['destination']
    total = route_result['total_stations']
    changes = route_result['interchanges']
    steps = route_result['steps']
    
    lines = []
    lines.append(f"🚇 **Metro Route: {src} ➝ {dst}**")
    lines.append(f"⏱️  Total Stations: {total}")
    lines.append(f"🔀  Interchanges: {changes}")
    lines.append("-" * 40)
    
    for i, step in enumerate(steps):
        lines.append(f"**Step {i+1}:** Board {step['line']}")
        lines.append(f"   📍 From: {step['start']}")
        lines.append(f"   🏁 To:   {step['end']}")
        lines.append(f"   🚋 Ride: {step['stops']} stops")
        
        if i < len(steps) - 1:
            lines.append("\n   🔄 **CHANGE TRAIN** ⬇️\n")
            
    lines.append("-" * 40)
    lines.append("✅ End of Route")
    
    return "\n".join(lines)

if __name__ == "__main__":
    # Test Validation Logic
    print(f"Valid 'Rajiv Chowk': {validate_station('rajiv chowk')}")
    print(f"Typo 'Noida Sec 18': {validate_station('noida sec 18')}")
    print(f"Invalid 'Mars Stn':  {validate_station('Mars Station')}")