import sys
import os

# Ensure we can import from current directory
sys.path.append(os.getcwd())

from dmrc_helpers import validate_station, format_route_text
from dmrc_routing import find_route

# ==========================================
# PART 5: SYSTEM TESTS & EXAMPLES
# ==========================================

def run_tests():
    print("==========================================")
    print("    DMRC ROUTE FINDER - SYSTEM TEST       ")
    print("==========================================\n")

    # -------------------------------------------------
    # TEST 1: Station Validation
    # -------------------------------------------------
    print("TEST 1: Station Validation")
    print("-" * 30)
    
    test_stations = [
        "Rajiv Chowk",      # Exact match
        "rajiv chowk",      # Case insensitive
        "Noida Sec 18",     # Typo (should match Noida Sector 18)
        "Mars Station"      # Invalid
    ]

    for name in test_stations:
        is_valid, result = validate_station(name)
        status = "✅ Found" if is_valid else "❌ Not Found"
        
        # If not valid but result exists, it's a suggestion
        if not is_valid and result:
            status = f"💡 Suggestion: {result}"
            
        print(f"Input: '{name}' -> {status}")
    print("\n")

    # -------------------------------------------------
    # TEST 2: Route Finding (Same Line)
    # -------------------------------------------------
    print("TEST 2: Route Finding (Same Line)")
    print("-" * 30)
    
    src = "Hauz Khas"
    dst = "Saket" # Both on Yellow Line
    
    print(f"Attempting Route: {src} -> {dst}")
    route = find_route(src, dst)
    print(format_route_text(route))
    print("\n")

    # -------------------------------------------------
    # TEST 3: Route Finding (With Interchange)
    # -------------------------------------------------
    print("TEST 3: Route Finding (With Interchange)")
    print("-" * 30)
    
    # Noida City Centre (Blue) -> Hauz Khas (Yellow/Magenta)
    # Expected: Blue -> Botanical Garden -> Magenta -> Hauz Khas (Fewest stops)
    # OR: Blue -> Rajiv Chowk -> Yellow -> Hauz Khas
    
    src = "Noida City Centre"
    dst = "Hauz Khas"         
    
    print(f"Attempting Route: {src} -> {dst}")
    route = find_route(src, dst)
    print(format_route_text(route))
    print("\n")

    # -------------------------------------------------
    # TEST 4: Error Handling
    # -------------------------------------------------
    print("TEST 4: Error Handling")
    print("-" * 30)
    
    route = find_route("Rajiv Chowk", "Mars Station")
    print(f"Result for Invalid Destination: {route}")
    print(format_route_text(route))

if __name__ == "__main__":
    run_tests()