"""
Routing Integration with StationLoader and FastAPI
Shows how to use routing algorithms with your DMRC chatbot
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from station_loader import StationLoader
import routing

# Initialize
app = FastAPI()
station_loader = StationLoader("dmrc_stations_dataset.csv")

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class RouteRequest(BaseModel):
    from_station: str
    to_station: str

class RouteResponse(BaseModel):
    from_station: str
    to_station: str
    bfs_path: list  # Fewest stations
    dijkstra: dict  # Shortest distance (if available)
    num_stations: int
    total_distance_km: float = None

class AutocompleteResponse(BaseModel):
    query: str
    results: list

class NearbyResponse(BaseModel):
    count: int
    stations: list

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.post("/api/route")
def get_route(request: RouteRequest):
    """
    Find route between two stations using both BFS and Dijkstra.
    
    Returns:
    - bfs_path: Route with fewest stations
    - dijkstra: Route with shortest distance (requires coordinates)
    """
    from_station = request.from_station
    to_station = request.to_station
    
    # Validate stations exist
    if from_station not in station_loader.stations:
        raise HTTPException(status_code=404, detail=f"Station '{from_station}' not found")
    if to_station not in station_loader.stations:
        raise HTTPException(status_code=404, detail=f"Station '{to_station}' not found")
    
    # Try BFS (fewest stations)
    bfs_path = routing.bfs_shortest_path(
        station_loader.graph, 
        from_station, 
        to_station
    )
    
    # Try Dijkstra (shortest distance)
    dijkstra_result = routing.dijkstra(
        station_loader.graph, 
        from_station, 
        to_station
    )
    
    # Format response
    response = {
        "from_station": from_station,
        "to_station": to_station,
        "bfs_path": bfs_path,
        "dijkstra": None,
        "num_stations": len(bfs_path) if bfs_path else 0,
        "total_distance_km": None,
        "message": None
    }
    
    if dijkstra_result:
        distance, path = dijkstra_result
        response["dijkstra"] = {
            "distance_km": round(distance, 2),
            "path": path,
            "num_stations": len(path)
        }
        response["total_distance_km"] = round(distance, 2)
    elif not bfs_path:
        response["message"] = "No route found between these stations"
    else:
        response["message"] = "Route found with BFS (no distance data available)"
    
    return response


@app.get("/api/autocomplete")
def autocomplete(q: str, limit: int = 10):
    """
    Autocomplete station names based on substring search.
    """
    if not q or len(q) < 1:
        return {"query": q, "results": []}
    
    search_results = station_loader.search(q)
    results = [s['name'] for s in search_results[:limit]]
    
    return {
        "query": q,
        "results": results,
        "total": len(results)
    }


@app.get("/api/nearby")
def nearby_stations(lat: float, lon: float, radius_km: float = 1.0, limit: int = 10):
    """
    Find stations near a geographic location.
    Requires latitude/longitude data in CSV.
    """
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise HTTPException(status_code=400, detail="Invalid coordinates")
    
    results = station_loader.nearby(lat, lon, radius_km)
    
    stations = []
    for distance, station in results[:limit]:
        stations.append({
            "name": station['name'],
            "distance_km": round(distance, 3),
            "lines": station['lines']
        })
    
    return {
        "latitude": lat,
        "longitude": lon,
        "radius_km": radius_km,
        "count": len(stations),
        "stations": stations
    }


@app.get("/api/station/{station_name}")
def get_station_info(station_name: str):
    """
    Get detailed information about a station.
    """
    station = station_loader.get_station(station_name)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    
    # Find adjacent stations
    neighbors = station_loader.get_neighbors(station_name)
    reachable = routing.get_connected_component(station_loader.graph, station_name)
    
    return {
        "name": station['name'],
        "lines": station['lines'],
        "is_interchange": len(station['lines']) > 1,
        "num_lines": len(station['lines']),
        "coordinates": station['coordinates'],
        "adjacent_stations": len(neighbors),
        "reachable_stations": len(reachable),
        "neighbors": [
            {"name": n, "distance_km": round(d, 2)} 
            for n, d in sorted(neighbors.items(), key=lambda x: x[1])[:5]
        ]
    }


@app.get("/api/line/{line_name}")
def get_line_info(line_name: str):
    """
    Get all stations on a specific metro line.
    """
    stations = station_loader.get_line_stations(line_name)
    if not stations:
        raise HTTPException(status_code=404, detail="Line not found")
    
    return {
        "line": line_name,
        "total_stations": len(stations),
        "start_station": stations[0],
        "end_station": stations[-1],
        "stations": stations
    }


@app.get("/api/interchange/{station_name}")
def get_interchange_info(station_name: str):
    """
    Get information about interchange points reachable from a station.
    """
    station = station_loader.get_station(station_name)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    
    if len(station['lines']) < 2:
        return {
            "station": station_name,
            "is_interchange": False,
            "message": f"{station_name} is not an interchange"
        }
    
    return {
        "station": station_name,
        "is_interchange": True,
        "lines": station['lines'],
        "num_lines": len(station['lines']),
        "can_interchange_to": [
            {"line": line, "stations": len(station_loader.get_line_stations(line))}
            for line in station['lines']
        ]
    }


@app.post("/api/check-reachability")
def check_reachability(from_station: str, to_station: str):
    """
    Check if two stations are connected (reachable).
    """
    if from_station not in station_loader.stations:
        raise HTTPException(status_code=404, detail=f"Station '{from_station}' not found")
    if to_station not in station_loader.stations:
        raise HTTPException(status_code=404, detail=f"Station '{to_station}' not found")
    
    is_reachable = routing.is_reachable(station_loader.graph, from_station, to_station)
    
    if is_reachable:
        # Find common lines (direct route)
        from_lines = set(station_loader.get_station(from_station)['lines'])
        to_lines = set(station_loader.get_station(to_station)['lines'])
        common_lines = from_lines & to_lines
        
        if common_lines:
            return {
                "reachable": True,
                "direct_route": True,
                "via_line": list(common_lines)[0],
                "message": f"You can take the {list(common_lines)[0]} line directly"
            }
        else:
            return {
                "reachable": True,
                "direct_route": False,
                "interchange_needed": True,
                "message": "You need to change lines to complete this journey"
            }
    else:
        return {
            "reachable": False,
            "message": "These stations are not connected in the network"
        }


# ============================================================================
# INTEGRATION WITH CHATBOT INTENTS
# ============================================================================

def handle_route_intent(from_station: str, to_station: str) -> str:
    """
    Handle chatbot route query intent.
    """
    if from_station not in station_loader.stations:
        return f"I don't recognize station '{from_station}'"
    if to_station not in station_loader.stations:
        return f"I don't recognize station '{to_station}'"
    
    # Check if stations exist on same line (direct route)
    from_lines = set(station_loader.get_station(from_station)['lines'])
    to_lines = set(station_loader.get_station(to_station)['lines'])
    common = from_lines & to_lines
    
    if common:
        return (f"You can go from {from_station} to {to_station} directly on the "
                f"{list(common)[0].upper()} line.")
    
    # Try BFS for fewest stations
    path = routing.bfs_shortest_path(station_loader.graph, from_station, to_station)
    
    if path:
        if len(path) == 2:
            return f"Take {from_station} to {to_station} (adjacent stations)"
        else:
            interchange = path[1]  # First interchange point
            return (f"Take {from_station}, interchange at {interchange}, "
                   f"then go to {to_station} ({len(path)-1} changes)")
    
    return "I cannot find a route between these stations"


def handle_station_info_intent(station_name: str) -> str:
    """
    Handle chatbot station info intent.
    """
    station = station_loader.get_station(station_name)
    
    if not station:
        # Try fuzzy search
        results = station_loader.search(station_name.lower())
        if results:
            return f"Did you mean: {results[0]['name']}?"
        return f"I don't know about {station_name}"
    
    lines_str = ", ".join(station['lines']).upper()
    is_interchange = "yes" if len(station['lines']) > 1 else "no"
    
    return f"{station['name']} is on the {lines_str} line(s). Interchange: {is_interchange}"


# ============================================================================
# EXAMPLE USAGE IN MAIN.PY
# ============================================================================

if __name__ == "__main__":
    print("Routing Integration Guide")
    print("=" * 60)
    print("\nAdd these to your main.py:\n")
    print("""
from routing_integration import (
    app, 
    handle_route_intent,
    handle_station_info_intent
)

# Then in your chatbot handler:
if intent == "route_query":
    response = handle_route_intent(from_station, to_station)
elif intent == "station_info":
    response = handle_station_info_intent(station_name)
    """)
    print("\nAvailable endpoints:")
    print("  POST  /api/route")
    print("  GET   /api/autocomplete?q=...")
    print("  GET   /api/nearby?lat=...&lon=...")
    print("  GET   /api/station/{name}")
    print("  GET   /api/line/{name}")
    print("  GET   /api/interchange/{name}")
    print("  POST  /api/check-reachability")
