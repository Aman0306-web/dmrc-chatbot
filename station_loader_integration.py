"""
INTEGRATION GUIDE: Using StationLoader with FastAPI
====================================================

This file shows how to integrate the StationLoader class into your 
existing main.py for enhanced station queries and route finding.

Example usage patterns:
1. Station info lookups (replace string-based search)
2. Line-based station navigation
3. Finding adjacent stations
4. Best-match station lookup with fuzzy search
"""

from station_loader import StationLoader
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Initialize loader at startup
loader = StationLoader("dmrc_stations_dataset.csv")

# ============================================================================
# EXAMPLE 1: Enhanced station info endpoint
# ============================================================================
class StationInfoRequest(BaseModel):
    station_name: str

def get_enhanced_station_info(station_name: str) -> dict:
    """
    Get comprehensive station information including:
    - All metro lines serving the station
    - Adjacent stations on each line
    - Whether it's an interchange
    """
    station = loader.get_station(station_name)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    
    response = {
        "name": station['name'],
        "lines": station['lines'],
        "coordinates": station['coordinates'],
        "is_interchange": len(station['lines']) > 1,
        "lines_detail": {}
    }
    
    # Get neighbors on each line
    for line in station['lines']:
        line_stations = loader.get_line_stations(line)
        if station['name'] in line_stations:
            idx = line_stations.index(station['name'])
            response['lines_detail'][line] = {
                "position_on_line": idx + 1,
                "total_stations": len(line_stations),
                "next_station": line_stations[idx + 1] if idx < len(line_stations) - 1 else None,
                "prev_station": line_stations[idx - 1] if idx > 0 else None,
            }
    
    return response


# ============================================================================
# EXAMPLE 2: List all stations on a specific line
# ============================================================================
def get_line_route(line: str) -> dict:
    """Get complete route for a metro line with all stations in order"""
    stations = loader.get_line_stations(line)
    if not stations:
        raise HTTPException(status_code=404, detail="Line not found")
    
    return {
        "line": line,
        "total_stations": len(stations),
        "stations": stations,
        "start_station": stations[0],
        "end_station": stations[-1]
    }


# ============================================================================
# EXAMPLE 3: Find interchange stations
# ============================================================================
def get_interchange_stations() -> dict:
    """Get all stations that serve multiple metro lines"""
    interchanges = [s for s in loader.stations.values() 
                   if len(s['lines']) > 1]
    
    return {
        "total_interchanges": len(interchanges),
        "interchanges": [
            {
                "name": s['name'],
                "lines": s['lines'],
                "num_lines": len(s['lines'])
            }
            for s in sorted(interchanges, key=lambda x: len(x['lines']), reverse=True)
        ]
    }


# ============================================================================
# EXAMPLE 4: Search stations (improved with fuzzy matching)
# ============================================================================
def search_stations(query: str) -> dict:
    """
    Search for stations with the given query.
    Uses fuzzy matching via the search method.
    """
    results = loader.search(query)
    
    return {
        "query": query,
        "total_results": len(results),
        "stations": [
            {
                "name": s['name'],
                "lines": s['lines'],
                "is_interchange": len(s['lines']) > 1
            }
            for s in results
        ]
    }


# ============================================================================
# EXAMPLE 5: Get all available lines
# ============================================================================
def get_all_lines() -> dict:
    """Get list of all available metro lines with station counts"""
    lines_info = []
    for line in loader.list_all_lines():
        stations = loader.get_line_stations(line)
        lines_info.append({
            "name": line,
            "total_stations": len(stations),
            "start": stations[0] if stations else None,
            "end": stations[-1] if stations else None
        })
    
    return {
        "total_lines": len(lines_info),
        "lines": lines_info
    }


# ============================================================================
# EXAMPLE 6: Station-to-station relationships
# ============================================================================
def get_adjacent_stations(station_name: str) -> dict:
    """Get all adjacent stations (neighbors in the graph)"""
    station = loader.get_station(station_name)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    
    neighbors = loader.get_neighbors(station_name)
    
    return {
        "station": station_name,
        "adjacent_count": len(neighbors),
        "adjacent_stations": [
            {
                "name": neighbor,
                "distance_km": distance
            }
            for neighbor, distance in sorted(neighbors.items(), key=lambda x: x[1])
        ]
    }


# ============================================================================
# HOW TO ADD THESE TO main.py
# ============================================================================
"""
In your main.py, add the following routes:

from station_loader import StationLoader

app = FastAPI()

# Initialize at startup
loader = StationLoader("dmrc_stations_dataset.csv")

@app.get("/api/station/{station_name}")
def station_info(station_name: str):
    return get_enhanced_station_info(station_name)

@app.get("/api/line/{line}")
def line_route(line: str):
    return get_line_route(line)

@app.get("/api/interchanges")
def interchanges():
    return get_interchange_stations()

@app.get("/api/search")
def search(q: str):
    return search_stations(q)

@app.get("/api/lines")
def all_lines():
    return get_all_lines()

@app.get("/api/adjacent/{station_name}")
def adjacent(station_name: str):
    return get_adjacent_stations(station_name)
"""

# ============================================================================
# QUICK REFERENCE - StationLoader API
# ============================================================================
"""
StationLoader Methods:

1. get_station(name: str) -> dict
   Returns station object with name, lines, coordinates, meta
   
2. search(query: str) -> list[dict]
   Returns stations whose name contains the query (case-insensitive)
   
3. nearby(lat: float, lon: float, radius_km: float) -> list[tuple]
   Returns (distance, station) tuples within radius
   Requires coordinate data in CSV
   
4. get_line_stations(line: str) -> list[str]
   Returns ordered list of all stations on a specific line
   
5. get_neighbors(station: str) -> dict[str, float]
   Returns adjacent stations: {station_name: distance_km}
   Graph connectivity depends on coordinate data
   
6. get_distance(station1: str, station2: str) -> float
   Returns distance between adjacent stations
   
7. list_all_lines() -> list[str]
   Returns all metro lines in the system
   
8. _normalize(name: str) -> str
   Standardizes station name for lookups (internal use)
"""

if __name__ == "__main__":
    # Quick test
    print("Station Loader Integration Module")
    print("-----------------------------------")
    print("All functions defined and ready to use")
    print("Import this module in main.py and use the examples above")
    print()
    print("Available functions:")
    print("- get_enhanced_station_info()")
    print("- get_line_route()")
    print("- get_interchange_stations()")
    print("- search_stations()")
    print("- get_all_lines()")
    print("- get_adjacent_stations()")
