"""
Routing Module - Quick Reference Card
Copy-paste solutions for common tasks
"""

# ============================================================================
# 1. BASIC SETUP
# ============================================================================

from station_loader import StationLoader
import routing

loader = StationLoader("dmrc_master_stations.csv")
# Ready to route!


# ============================================================================
# 2. FIND FEWEST STATIONS ROUTE (BFS)
# ============================================================================

from routing import bfs_shortest_path

path = bfs_shortest_path(loader.graph, "Rajiv Chowk", "Connaught Place")
if path:
    print("Route:", " -> ".join(path))
    print("Stations:", len(path))
else:
    print("No route found")


# ============================================================================
# 3. FIND SHORTEST DISTANCE ROUTE (DIJKSTRA)
# ============================================================================

from routing import dijkstra

result = dijkstra(loader.graph, "Rajiv Chowk", "Connaught Place")
if result:
    distance, path = result
    print("Route:", " -> ".join(path))
    print("Distance: {:.2f}km".format(distance))
    print("Stations:", len(path))


# ============================================================================
# 4. CHECK FOR DIRECT LINE TRANSFER
# ============================================================================

def has_direct_line(station_a, station_b):
    a = loader.get_station(station_a)
    b = loader.get_station(station_b)
    if not a or not b:
        return False, None
    common = set(a['lines']) & set(b['lines'])
    return len(common) > 0, list(common)[0] if common else None

is_direct, line = has_direct_line("Rajiv Chowk", "Connaught Place")
if is_direct:
    print("Direct via {} line".format(line.upper()))
else:
    print("Need to interchange")


# ============================================================================
# 5. FIND ALL ALTERNATIVE ROUTES
# ============================================================================

from routing import get_all_paths_limited

paths = get_all_paths_limited(loader.graph, "Rajiv Chowk", "Connaught Place", max_length=5)
print("Found {} alternative routes".format(len(paths)))
for i, path in enumerate(paths, 1):
    print("Route {}: {}".format(i, " -> ".join(path)))


# ============================================================================
# 6. FIND INTERCHANGE POINT
# ============================================================================

from routing import find_nearest_common_station

interchange = find_nearest_common_station(loader.graph, "Station A", "Station B")
if interchange:
    print("Interchange at: {}".format(interchange))


# ============================================================================
# 7. CHECK IF TWO STATIONS ARE CONNECTED
# ============================================================================

from routing import is_reachable

if is_reachable(loader.graph, "Rajiv Chowk", "Connaught Place"):
    print("Connected!")
else:
    print("Not connected")


# ============================================================================
# 8. FIND ALL REACHABLE STATIONS FROM A STATION
# ============================================================================

from routing import get_connected_component

reachable = get_connected_component(loader.graph, "Rajiv Chowk")
print("Can reach {} stations".format(len(reachable)))


# ============================================================================
# 9. INTELLIGENT ROUTE PLANNING
# ============================================================================

def get_best_route(station_a, station_b):
    """Suggest the best route based on available options"""
    
    # Check direct line
    a = loader.get_station(station_a)
    b = loader.get_station(station_b)
    
    if not a or not b:
        return {"error": "Station not found"}
    
    common_lines = set(a['lines']) & set(b['lines'])
    
    if common_lines:
        return {
            "type": "direct",
            "line": list(common_lines)[0].upper(),
            "message": "Take {} line directly".format(list(common_lines)[0].upper())
        }
    
    # Try BFS
    bfs_path = bfs_shortest_path(loader.graph, station_a, station_b)
    if bfs_path:
        return {
            "type": "fewest_stations",
            "path": bfs_path,
            "stations": len(bfs_path),
            "message": "Route via {} stations".format(len(bfs_path))
        }
    
    # Try Dijkstra
    dijkstra_result = dijkstra(loader.graph, station_a, station_b)
    if dijkstra_result:
        distance, path = dijkstra_result
        return {
            "type": "shortest_distance",
            "path": path,
            "distance_km": distance,
            "message": "Route via {:.1f}km".format(distance)
        }
    
    return {"error": "No route found"}

result = get_best_route("Rajiv Chowk", "Connaught Place")
print(result["message"])


# ============================================================================
# 10. ROUTE WITH INTERCHANGE SUGGESTION
# ============================================================================

def route_with_details(from_station, to_station):
    """Show detailed route with interchange info"""
    
    a = loader.get_station(from_station)
    b = loader.get_station(to_station)
    
    if not a or not b:
        return "Station not found"
    
    # Direct line
    common = set(a['lines']) & set(b['lines'])
    if common:
        line = list(common)[0]
        stations_on_line = loader.get_line_stations(line)
        a_idx = stations_on_line.index(from_station)
        b_idx = stations_on_line.index(to_station)
        num_stops = abs(b_idx - a_idx)
        
        result = "Take {} line from {} to {}".format(line.upper(), from_station, to_station)
        result += "\nStops: {}".format(num_stops)
        return result
    
    # Via interchange
    path = bfs_shortest_path(loader.graph, from_station, to_station)
    if path and len(path) > 2:
        interchange = path[1]
        interchange_lines_a = set(loader.get_station(path[0])['lines']) & set(loader.get_station(interchange)['lines'])
        interchange_lines_b = set(loader.get_station(interchange)['lines']) & set(loader.get_station(path[2])['lines'])
        
        result = "Route: {} -> {} -> {}".format(from_station, interchange, to_station)
        if interchange_lines_a:
            result += "\nTake {} line to {}".format(list(interchange_lines_a)[0].upper(), interchange)
        if interchange_lines_b:
            result += "\nChange to {} line to {}".format(list(interchange_lines_b)[0].upper(), to_station)
        return result
    
    return "Path: " + " -> ".join(path) if path else "No route found"

print(route_with_details("Rajiv Chowk", "Khanpur"))


# ============================================================================
# 11. FASTAPI SETUP
# ============================================================================

"""
In your main.py, add:

from routing_integration import (
    get_route,
    autocomplete,
    nearby_stations,
    get_station_info,
    get_line_info,
    get_interchange_info,
    check_reachability,
    handle_route_intent,
    handle_station_info_intent
)

@app.post("/api/route")
async def route(request: RouteRequest):
    return get_route(request)

@app.get("/api/autocomplete")
async def auto(q: str):
    return autocomplete(q)

# ... add other endpoints
"""


# ============================================================================
# 12. CHATBOT INTEGRATION
# ============================================================================

def route_chatbot_response(intent, from_station, to_station):
    """Generate chatbot response for route queries"""
    
    if intent == "route_query":
        return route_with_details(from_station, to_station)
    
    elif intent == "can_go":
        if is_reachable(loader.graph, from_station, to_station):
            a = loader.get_station(from_station)
            b = loader.get_station(to_station)
            common = set(a['lines']) & set(b['lines'])
            if common:
                return "Yes, take {} line directly".format(list(common)[0].upper())
            else:
                return "Yes, but you need to interchange"
        else:
            return "No, these stations are not connected"
    
    elif intent == "station_info":
        station = loader.get_station(from_station)
        if station:
            lines = ", ".join([l.upper() for l in station['lines']])
            return "{} is on: {}".format(from_station, lines)
        return "Station not found"


# ============================================================================
# 13. ERROR HANDLING
# ============================================================================

def safe_route_query(from_station, to_station):
    """Route query with proper error handling"""
    try:
        # Validate stations exist
        if from_station not in loader.stations:
            return {"error": "Start station not found"}
        if to_station not in loader.stations:
            return {"error": "End station not found"}
        
        # Try to find route
        path = bfs_shortest_path(loader.graph, from_station, to_station)
        
        if path:
            return {
                "success": True,
                "path": path,
                "stations": len(path)
            }
        else:
            return {
                "success": False,
                "error": "No route found between stations"
            }
    
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# 14. BATCH PROCESSING
# ============================================================================

def batch_route_planning(route_list):
    """Process multiple route queries at once"""
    results = []
    for from_st, to_st in route_list:
        path = bfs_shortest_path(loader.graph, from_st, to_st)
        results.append({
            "from": from_st,
            "to": to_st,
            "path": path,
            "stations": len(path) if path else None
        })
    return results

routes = [
    ("Rajiv Chowk", "Connaught Place"),
    ("Central Secretariat", "New Delhi"),
    ("Chandni Chowk", "Kasturba Nagar")
]

for result in batch_route_planning(routes):
    if result['path']:
        print("{} -> {}: {} stations".format(result['from'], result['to'], result['stations']))


# ============================================================================
# 15. NETWORK ANALYSIS
# ============================================================================

def analyze_network():
    """Analyze DMRC network structure"""
    
    # Find most connected stations
    connectivity = {}
    for station_name in loader.stations.keys():
        reachable = get_connected_component(loader.graph, station_name)
        connectivity[station_name] = len(reachable)
    
    most_connected = sorted(connectivity.items(), key=lambda x: x[1], reverse=True)[:5]
    print("Most connected stations:")
    for station, count in most_connected:
        print("  {}: can reach {}".format(station, count))
    
    # Find isolated stations
    for station in loader.stations.keys():
        if connectivity[station] == 1:
            print("Isolated: {}".format(station))

# analyze_network()


if __name__ == "__main__":
    # Quick test
    print("Routing Module Quick Reference")
    print("------------------------------")
    print("All functions ready to use!")
    print("\nExample: BFS route from Rajiv Chowk to Connaught Place")
    
    path = bfs_shortest_path(loader.graph, "Rajiv Chowk", "Connaught Place")
    if path:
        print("Found: {} -> {} stations".format(" -> ".join(path), len(path)))
    else:
        print("Note: Graph is empty (no coordinates in CSV yet)")
