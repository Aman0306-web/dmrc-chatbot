"""
Fuzzy Search Integration with StationLoader and FastAPI
Demonstrates fuzzy matching for improved station discovery
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from station_loader import StationLoader
from fuzzy_search import (
    fuzzy_search_station,
    autocomplete_station,
    best_match_station,
    fuzzy_search_with_scorer
)

# Initialize
app = FastAPI()
loader = StationLoader("dmrc_master_stations.csv")

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class FuzzySearchRequest(BaseModel):
    query: str
    limit: int = 8
    threshold: int = 60

class FuzzySearchResponse(BaseModel):
    query: str
    results: list
    total: int

# ============================================================================
# ENDPOINTS WITH FUZZY SEARCH
# ============================================================================

@app.get("/api/fuzzy-search")
def fuzzy_search(q: str, limit: int = 8, threshold: int = 60):
    """
    Search stations with fuzzy matching (typo-tolerant).
    
    Example:
        /api/fuzzy-search?q=rajeev+chok&limit=5
    """
    if not q or len(q) < 1:
        return {"query": q, "results": [], "total": 0}
    
    station_names = list(loader.stations.keys())
    results = fuzzy_search_station(q, station_names, limit=limit, threshold=threshold)
    
    # Enhance results with station details
    enhanced = []
    for r in results:
        station = loader.get_station(r["name"])
        if station:
            enhanced.append({
                "name": r["name"],
                "score": round(r["score"], 2),
                "lines": station['lines'],
                "is_interchange": len(station['lines']) > 1
            })
    
    return {
        "query": q,
        "results": enhanced,
        "total": len(enhanced),
        "threshold": threshold
    }


@app.get("/api/autocomplete")
def autocomplete(q: str, limit: int = 5):
    """
    Autocomplete station names with fuzzy matching.
    
    Example:
        /api/autocomplete?q=khan&limit=5
    """
    if not q or len(q) < 1:
        return {"query": q, "suggestions": [], "total": 0}
    
    station_names = list(loader.stations.keys())
    suggestions = autocomplete_station(q, station_names, limit=limit)
    
    return {
        "query": q,
        "suggestions": suggestions,
        "total": len(suggestions)
    }


@app.get("/api/best-match")
def best_match(q: str):
    """
    Find single best matching station.
    
    Example:
        /api/best-match?q=chandi+chawk
    """
    if not q:
        raise HTTPException(status_code=400, detail="Query required")
    
    station_names = list(loader.stations.keys())
    best = best_match_station(q, station_names)
    
    if not best:
        raise HTTPException(status_code=404, detail="No matching station found")
    
    station = loader.get_station(best)
    
    return {
        "query": q,
        "best_match": best,
        "lines": station['lines'],
        "is_interchange": len(station['lines']) > 1
    }


@app.get("/api/fuzzy-search-advanced")
def fuzzy_search_advanced(q: str, scorer: str = "WRatio", limit: int = 8):
    """
    Advanced fuzzy search with selectable scoring algorithm.
    
    Scorers:
    - WRatio: Best overall (default)
    - TokenSort: Handles word order
    - PartialRatio: Substring matching
    - TokenSet: Handles duplicates
    
    Example:
        /api/fuzzy-search-advanced?q=delhi+gate&scorer=TokenSort&limit=5
    """
    valid_scorers = ["WRatio", "Ratio", "PartialRatio", "TokenSort", "TokenSet"]
    
    if scorer not in valid_scorers:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid scorer. Valid: {', '.join(valid_scorers)}"
        )
    
    if not q:
        return {"query": q, "results": [], "scorer": scorer, "total": 0}
    
    station_names = list(loader.stations.keys())
    results = fuzzy_search_with_scorer(q, station_names, scorer=scorer, limit=limit)
    
    # Enhance results
    enhanced = []
    for r in results:
        station = loader.get_station(r["name"])
        if station:
            enhanced.append({
                "name": r["name"],
                "score": round(r["score"], 2),
                "lines": station['lines']
            })
    
    return {
        "query": q,
        "scorer": scorer,
        "results": enhanced,
        "total": len(enhanced)
    }


# ============================================================================
# SMART STATION LOOKUP
# ============================================================================

def smart_station_lookup(query: str) -> dict:
    """
    Smart lookup combining multiple strategies.
    
    Strategy:
    1. Exact match
    2. Case-insensitive match
    3. Fuzzy match
    4. Best match
    """
    # Strategy 1: Exact match
    station = loader.get_station(query)
    if station:
        return {
            "found": True,
            "method": "exact",
            "station": station
        }
    
    # Strategy 2: Case-insensitive match
    for name, station_data in loader.stations.items():
        if name.lower() == query.lower():
            return {
                "found": True,
                "method": "case-insensitive",
                "station": station_data
            }
    
    # Strategy 3: Fuzzy match
    station_names = list(loader.stations.keys())
    results = fuzzy_search_station(query, station_names, limit=1, threshold=70)
    
    if results:
        station = loader.get_station(results[0]["name"])
        return {
            "found": True,
            "method": "fuzzy",
            "confidence": results[0]["score"],
            "station": station
        }
    
    # Strategy 4: Best match (lower threshold)
    results = fuzzy_search_station(query, station_names, limit=1, threshold=40)
    
    if results:
        station = loader.get_station(results[0]["name"])
        return {
            "found": True,
            "method": "best_match",
            "confidence": results[0]["score"],
            "station": station,
            "message": "Did you mean: {}?".format(results[0]["name"])
        }
    
    return {
        "found": False,
        "method": "none",
        "message": "No matching station found"
    }


@app.get("/api/smart-lookup")
def smart_lookup(q: str):
    """
    Smart station lookup with multiple strategies.
    
    Example:
        /api/smart-lookup?q=rajiv+chok
    """
    if not q:
        raise HTTPException(status_code=400, detail="Query required")
    
    result = smart_station_lookup(q)
    
    if not result["found"]:
        return {
            "query": q,
            "found": False,
            "message": result["message"],
            "suggestions": autocomplete_station(q, list(loader.stations.keys()), limit=3)
        }
    
    station = result["station"]
    return {
        "query": q,
        "found": True,
        "method": result["method"],
        "confidence": result.get("confidence"),
        "station": {
            "name": station['name'],
            "lines": station['lines'],
            "is_interchange": len(station['lines']) > 1,
            "num_lines": len(station['lines'])
        },
        "message": result.get("message")
    }


# ============================================================================
# INTEGRATION WITH CHATBOT
# ============================================================================

def chatbot_station_handler(user_query: str) -> str:
    """
    Handle chatbot station queries with fuzzy matching.
    """
    # Try exact match first
    station = loader.get_station(user_query)
    
    if not station:
        # Try fuzzy match
        result = smart_station_lookup(user_query)
        if not result["found"]:
            return (f"I couldn't find '{user_query}'. Did you mean: "
                   f"{', '.join(autocomplete_station(user_query, list(loader.stations.keys()), limit=3))}?")
        station = result["station"]
    
    # Format response
    lines_str = ", ".join([l.upper() for l in station['lines']])
    interchange = "Yes, interchange available" if len(station['lines']) > 1 else "No"
    
    return (f"{station['name']} is on: {lines_str}. "
           f"Interchange: {interchange}")


# ============================================================================
# BATCH FUZZY SEARCH
# ============================================================================

@app.post("/api/batch-fuzzy-search")
def batch_fuzzy_search(queries: list):
    """
    Search multiple queries at once.
    
    Example:
        POST /api/batch-fuzzy-search
        ["rajiv chok", "khan market", "dil shed"]
    """
    if not queries:
        return {"queries": [], "results": []}
    
    station_names = list(loader.stations.keys())
    results = []
    
    for q in queries:
        matches = fuzzy_search_station(q, station_names, limit=3, threshold=50)
        enhanced = []
        for m in matches:
            station = loader.get_station(m["name"])
            if station:
                enhanced.append({
                    "name": m["name"],
                    "score": round(m["score"], 2),
                    "lines": station['lines']
                })
        
        results.append({
            "query": q,
            "matches": enhanced,
            "total": len(enhanced)
        })
    
    return {
        "total_queries": len(queries),
        "results": results
    }


# ============================================================================
# IMPLEMENTATION GUIDE
# ============================================================================

if __name__ == "__main__":
    print("Fuzzy Search Integration Guide")
    print("=" * 60)
    print("\nAdd these to your main.py:\n")
    print("""
from fuzzy_search_integration import (
    fuzzy_search,
    autocomplete,
    best_match,
    smart_lookup,
    batch_fuzzy_search,
    chatbot_station_handler
)

# Register endpoints:
app.include_router(...)

# Use in chatbot:
response = chatbot_station_handler("rajiv chok")
    """)
    
    print("\nAvailable endpoints:")
    print("  GET  /api/fuzzy-search")
    print("  GET  /api/autocomplete")
    print("  GET  /api/best-match")
    print("  GET  /api/fuzzy-search-advanced")
    print("  GET  /api/smart-lookup")
    print("  POST /api/batch-fuzzy-search")
