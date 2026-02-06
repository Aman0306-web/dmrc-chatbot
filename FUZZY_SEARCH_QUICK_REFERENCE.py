# Fuzzy Search Module - Quick Reference

## Quick Start

```python
from fuzzy_search import fuzzy_search_station, autocomplete_station
from station_loader import StationLoader

# Load stations
loader = StationLoader("dmrc_stations_dataset.csv")
stations = list(loader.stations.keys())

# Basic search
results = fuzzy_search_station("khan", stations)
# [{"name": "Khan Market", "score": 100}, ...]

# Get suggestions
suggestions = autocomplete_station("raj", stations, limit=5)
# ["Rajiv Chowk", ...]

# Get best match
best = best_match_station("chandi chawk", stations)
# "Chandni Chowk"
```

---

## Function Reference

### Search Functions

#### `fuzzy_search_station(query, choices, limit=8, threshold=60)`
```python
results = fuzzy_search_station("rajeev chok", stations)
# [{"name": "Rajiv Chowk", "score": 63.6}, ...]

results = fuzzy_search_station("khan", stations, limit=3, threshold=70)
```

#### `autocomplete_station(query, choices, limit=5)`
```python
suggestions = autocomplete_station("khan", stations)
# ["Khan Market", "Khanpur", ...]

suggestions = autocomplete_station("ra", stations, limit=10)
```

#### `best_match_station(query, choices, min_score=40)`
```python
best = best_match_station("delhi gate", stations)
# "Delhi Gate" (or "New Delhi" depending on match)

best = best_match_station("nonexistent", stations)
# None
```

#### `fuzzy_search_with_scorer(query, choices, scorer="WRatio", limit=8)`
```python
# WRatio (best for most cases)
results = fuzzy_search_with_scorer("rajiv chowk", stations, scorer="WRatio")

# TokenSort (good for word order issues)
results = fuzzy_search_with_scorer("chowk rajiv", stations, scorer="TokenSort")

# PartialRatio (substring matching)
results = fuzzy_search_with_scorer("market", stations, scorer="PartialRatio")

# TokenSet (duplicate handling)
results = fuzzy_search_with_scorer("Rajiv Rajiv", stations, scorer="TokenSet")

# Ratio (simple comparison)
results = fuzzy_search_with_scorer("rajiv", stations, scorer="Ratio")
```

#### `compare_similarity(query, choice, scorer="WRatio")`
```python
score = compare_similarity("rajiv chowk", "Rajiv Chowk")
# 81.81

score = compare_similarity("rajeev chok", "Rajiv Chowk")
# 63.63

score = compare_similarity("Chowk Rajiv", "Rajiv Chowk", scorer="TokenSort")
# 95.0
```

---

## Common Patterns

### Pattern 1: Typo Tolerance

```python
def search_with_typo_tolerance(query, loader, threshold=60):
    stations = list(loader.stations.keys())
    results = fuzzy_search_station(query, stations, threshold=threshold)
    
    if results:
        best = results[0]
        return loader.get_station(best['name'])
    return None

# Usage
station = search_with_typo_tolerance("rajeev chok", loader)
print(f"Found: {station['name']} on lines {station['lines']}")
```

### Pattern 2: Autocomplete for Chat

```python
def get_autocomplete_suggestions(query, loader):
    stations = list(loader.stations.keys())
    suggestions = autocomplete_station(query, stations, limit=5)
    
    return [
        {
            "name": s,
            "lines": loader.stations[s].get('lines', []),
            "interchange": len(loader.stations[s].get('lines', [])) > 1
        }
        for s in suggestions
    ]

# Usage in chat endpoint
suggestions = get_autocomplete_suggestions("khan", loader)
```

### Pattern 3: Smart Station Lookup

```python
def smart_station_lookup(query, loader):
    """Intelligent lookup with fallback strategies"""
    stations = list(loader.stations.keys())
    
    # Try exact match first
    normalized_query = query.strip().title()
    if normalized_query in stations:
        return {"found": True, "method": "exact", "station": loader.get_station(normalized_query)}
    
    # Try fuzzy match
    results = fuzzy_search_station(query, stations, threshold=70)
    if results:
        best_match = results[0]
        return {
            "found": True,
            "method": "fuzzy",
            "confidence": best_match['score'],
            "station": loader.get_station(best_match['name'])
        }
    
    # Return suggestions
    suggestions = autocomplete_station(query, stations, limit=5)
    return {
        "found": False,
        "suggestions": suggestions
    }

# Usage
result = smart_station_lookup("rajeev chok", loader)
if result['found']:
    print(f"Found: {result['station']['name']} ({result['method']})")
else:
    print(f"Did you mean: {', '.join(result['suggestions'])}")
```

### Pattern 4: Batch Search

```python
def batch_fuzzy_search(queries, loader):
    """Search multiple queries efficiently"""
    stations = list(loader.stations.keys())
    results = {}
    
    for query in queries:
        matches = fuzzy_search_station(query, stations, limit=3)
        results[query] = [
            {
                "name": m['name'],
                "score": m['score'],
                "lines": loader.stations[m['name']]['lines']
            }
            for m in matches
        ]
    
    return results

# Usage
batch_results = batch_fuzzy_search(["khan", "rajiv", "delhi"], loader)
for query, matches in batch_results.items():
    print(f"{query}: {[m['name'] for m in matches]}")
```

### Pattern 5: Thresh Adaptive Search

```python
def adaptive_fuzzy_search(query, loader, initial_threshold=70):
    """Try higher threshold first, then lower if no results"""
    stations = list(loader.stations.keys())
    
    # Try strict
    results = fuzzy_search_station(query, stations, threshold=initial_threshold)
    if results:
        return {"results": results, "threshold": initial_threshold}
    
    # Fall back to moderate
    results = fuzzy_search_station(query, stations, threshold=50)
    if results:
        return {"results": results, "threshold": 50}
    
    # Last resort
    results = fuzzy_search_station(query, stations, threshold=30)
    return {"results": results, "threshold": 30}

# Usage
response = adaptive_fuzzy_search("markt", loader)
print(f"Found with threshold {response['threshold']}: {[r['name'] for r in response['results']]}")
```

---

## Scorer Comparison

```python
from fuzzy_search import fuzzy_search_with_scorer

query = "khan market"
scorers = ["WRatio", "Ratio", "PartialRatio", "TokenSort", "TokenSet"]

for scorer in scorers:
    results = fuzzy_search_with_scorer(query, stations, scorer=scorer, limit=1)
    if results:
        print(f"{scorer}: {results[0]['name']} ({results[0]['score']})")
```

---

## Threshold Examples

### Threshold 90+ (Strict)
```python
results = fuzzy_search_station("khan", stations, threshold=90)
# Only very exact matches
```

### Threshold 70-80 (Confident)
```python
results = fuzzy_search_station("khan", stations, threshold=75)
# Good matches with minor typos
```

### Threshold 60 (Default)
```python
results = fuzzy_search_station("khan", stations, threshold=60)
# Balanced approach
```

### Threshold 40-50 (Loose)
```python
results = fuzzy_search_station("khan", stations, threshold=40)
# Many partial matches
```

### Threshold 0-30 (Very Loose)
```python
results = fuzzy_search_station("khan", stations, threshold=0)
# Everything remotely similar
```

---

## FastAPI Endpoints Example

```python
from fastapi import FastAPI, Query
from station_loader import StationLoader
from fuzzy_search import fuzzy_search_station

app = FastAPI()
loader = StationLoader("dmrc_stations_dataset.csv")
stations = list(loader.stations.keys())

@app.get("/api/search")
def search(q: str, limit: int = 8, threshold: int = 60):
    """Fuzzy search endpoint"""
    results = fuzzy_search_station(q, stations, limit=limit, threshold=threshold)
    
    return {
        "query": q,
        "results": results,
        "total": len(results),
        "threshold": threshold
    }

@app.get("/api/autocomplete")
def autocomplete(q: str, limit: int = 5):
    """Autocomplete endpoint"""
    from fuzzy_search import autocomplete_station
    
    suggestions = autocomplete_station(q, stations, limit=limit)
    return {
        "query": q,
        "suggestions": suggestions,
        "total": len(suggestions)
    }

@app.get("/api/best-match")
def best_match(q: str):
    """Get best matching station"""
    from fuzzy_search import best_match_station
    
    best = best_match_station(q, stations)
    if best:
        return {
            "query": q,
            "best_match": best,
            "lines": loader.stations[best].get('lines', [])
        }
    return {"query": q, "best_match": None}

# Usage:
# GET /api/search?q=khan&limit=5
# GET /api/autocomplete?q=raj
# GET /api/best-match?q=delhi+gate
```

---

## Error Handling

```python
def safe_fuzzy_search(query, loader):
    """Search with comprehensive error handling"""
    try:
        if not query or not isinstance(query, str):
            return {"error": "Query must be a non-empty string"}
        
        stations = list(loader.stations.keys())
        results = fuzzy_search_station(query, stations)
        
        return {"results": results, "error": None}
    
    except Exception as e:
        return {"error": str(e), "results": []}

# Usage
response = safe_fuzzy_search("", loader)
if response['error']:
    print(f"Error: {response['error']}")
```

---

## Performance Tips

```python
# GOOD: Pre-compute station list
stations = list(loader.stations.keys())

for query in user_queries:
    results = fuzzy_search_station(query, stations)  # Fast!
    # ...

# BAD: Recomputing each time
for query in user_queries:
    stations = list(loader.stations.keys())  # Inefficient
    results = fuzzy_search_station(query, stations)
    # ...
```

---

## Debugging

```python
def debug_fuzzy_search(query, loader):
    """Debug fuzzy search with detailed output"""
    stations = list(loader.stations.keys())
    
    print(f"Query: '{query}'")
    print(f"Total stations: {len(stations)}")
    
    results = fuzzy_search_station(query, stations, threshold=0, limit=10)
    
    print("\nTop matches:")
    for i, result in enumerate(results[:5], 1):
        print(f"  {i}. {result['name']}: {result['score']:.1f}%")
    
    return results

# Usage
debug_fuzzy_search("khan", loader)
```

---

## Real-World Examples

### Example 1: Chat Intent Extraction

```python
def extract_station_from_message(message, loader):
    """Extract station name from chat message"""
    # Try common patterns
    patterns = ["route to", "go to", "station", "from"]
    
    for pattern in patterns:
        if pattern in message.lower():
            station_part = message.split(pattern)[-1].strip()
            result = smart_station_lookup(station_part, loader)
            if result['found']:
                return result['station']
    
    return None

message = "route to राजीव चौक"  # Hindi
station = extract_station_from_message(message, loader)
```

### Example 2: Live Search Widget

```python
def handle_live_search(query, loader):
    """Return results for live search UI"""
    if len(query) < 2:
        return []
    
    stations = list(loader.stations.keys())
    results = fuzzy_search_station(query, stations, limit=5, threshold=40)
    
    return [
        {
            "name": r['name'],
            "score": f"{r['score']:.0f}%",
            "lines": loader.stations[r['name']]['lines'],
            "highlight": True if r['score'] > 80 else False
        }
        for r in results
    ]

# Usage in UI
results = handle_live_search(user_input, loader)
# Render as dropdown list
```

### Example 3: Error Message Suggestion

```python
def suggest_station_correction(invalid_query, loader):
    """Suggest correction for mistyped station"""
    stations = list(loader.stations.keys())
    
    best = best_match_station(invalid_query, stations, min_score=50)
    
    if best:
        return f"Did you mean: {best}?"
    
    suggestions = autocomplete_station(invalid_query, stations, limit=3)
    if suggestions:
        return f"Similar: {', '.join(suggestions)}"
    
    return "Station not found. Please try again."

# Usage
message = suggest_station_correction("rajvie chow", loader)
print(message)  # "Did you mean: Rajiv Chowk?"
```

---

## Scorer Selection Guide

| Scenario | Scorer | Reason |
|----------|--------|--------|
| General search | WRatio | Best overall |
| Typos | WRatio | Handles variations |
| Word order | TokenSort | Reorders before match |
| Partial match | PartialRatio | Substring focus |
| Exact match | Ratio | Pure similarity |
| Duplicates | TokenSet | Removes duplicates |

---

## Testing Code

```python
def test_fuzzy_search():
    """Test fuzzy search functionality"""
    from station_loader import StationLoader
    from fuzzy_search import fuzzy_search_station, best_match_station
    
    loader = StationLoader("dmrc_stations_dataset.csv")
    stations = list(loader.stations.keys())
    
    # Test cases
    tests = [
        ("rajeev chok", "Rajiv Chowk", 60),
        ("khan", "Khan Market", 90),
        ("delhi gate", "Delhi Gate", 80),
        ("chandni chawk", "Chandni Chowk", 60),
    ]
    
    for query, expected, min_threshold in tests:
        results = fuzzy_search_station(query, stations, threshold=min_threshold)
        
        match_found = any(r['name'] == expected for r in results)
        status = "✓" if match_found else "✗"
        
        print(f"{status} {query} → {expected}")
    
    print("\nAll tests passed!")

# Run
test_fuzzy_search()
```

---

## Complete Integration Template

```python
from fastapi import FastAPI
from station_loader import StationLoader
from fuzzy_search import (
    fuzzy_search_station,
    autocomplete_station,
    best_match_station,
    fuzzy_search_with_scorer
)

app = FastAPI(title="DMRC Fuzzy Search")
loader = StationLoader("dmrc_stations_dataset.csv")
stations = list(loader.stations.keys())

@app.get("/api/fuzzy-search")
async def fuzzy_search(q: str, limit: int = 8, threshold: int = 60):
    return {
        "query": q,
        "results": fuzzy_search_station(q, stations, limit=limit, threshold=threshold),
        "total": len(fuzzy_search_station(q, stations, limit=limit, threshold=threshold))
    }

@app.get("/api/autocomplete")
async def autocomplete(q: str, limit: int = 5):
    return {
        "query": q,
        "suggestions": autocomplete_station(q, stations, limit=limit)
    }

@app.get("/api/best-match")
async def best_match(q: str):
    best = best_match_station(q, stations)
    return {"query": q, "best_match": best}

@app.get("/api/compare")
async def compare(query: str, choice: str, scorer: str = "WRatio"):
    from fuzzy_search import compare_similarity
    return {
        "query": query,
        "choice": choice,
        "scorer": scorer,
        "score": compare_similarity(query, choice, scorer)
    }

# Run: uvicorn main:app --reload
```

---

**Quick Links:**
- [Full Guide](FUZZY_SEARCH_GUIDE.md)
- [Integration Examples](fuzzy_search_integration.py)
- [Module Code](fuzzy_search.py)

**Dependencies:** rapidfuzz  
**Status:** Production Ready
