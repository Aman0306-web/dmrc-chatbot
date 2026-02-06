"""
Fuzzy Search Module - Station lookup with typo tolerance
Uses RapidFuzz for advanced string matching
"""

from rapidfuzz import process, fuzz
from typing import List, Dict, Optional

def fuzzy_search_station(query: str, choices: List[str], limit: int = 8, 
                        threshold: int = 60) -> List[Dict]:
    """
    Search for stations with fuzzy matching (typo-tolerant).
    
    Args:
        query: Search query
        choices: List of station names to search
        limit: Maximum number of results
        threshold: Minimum match score (0-100)
    
    Returns:
        List of matching stations with scores
        
    Example:
        >>> results = fuzzy_search_station("rajeev chowk", station_list)
        >>> print(results[0])
        {'name': 'Rajiv Chowk', 'score': 95}
    """
    if not query or not choices:
        return []
    
    matches = process.extract(
        query, 
        choices, 
        scorer=fuzz.WRatio,  # Best overall string matching
        limit=limit,
        score_cutoff=threshold
    )
    
    return [{"name": m[0], "score": m[1]} for m in matches]


def fuzzy_search_with_scorer(query: str, choices: List[str], scorer: str = "WRatio",
                             limit: int = 8) -> List[Dict]:
    """
    Advanced fuzzy search with selectable scorer.
    
    Scorers:
    - WRatio: Best overall (default)
    - Ratio: Simple string similarity
    - PartialRatio: Substring matching
    - TokenSort: Handles word order
    - TokenSet: Handles duplicates
    
    Args:
        query: Search query
        choices: List of choices to search
        scorer: Scoring algorithm name
        limit: Maximum results
    
    Returns:
        List of matches with scores
    """
    if not query or not choices:
        return []
    
    scorer_map = {
        "WRatio": fuzz.WRatio,
        "Ratio": fuzz.ratio,
        "PartialRatio": fuzz.partial_ratio,
        "TokenSort": fuzz.token_sort_ratio,
        "TokenSet": fuzz.token_set_ratio,
    }
    
    scoring_func = scorer_map.get(scorer, fuzz.WRatio)
    
    matches = process.extract(
        query,
        choices,
        scorer=scoring_func,
        limit=limit
    )
    
    return [{"name": m[0], "score": m[1]} for m in matches]


def autocomplete_station(query: str, choices: List[str], limit: int = 5) -> List[str]:
    """
    Autocomplete station names with fuzzy matching.
    
    Args:
        query: Partial query
        choices: All station names
        limit: Maximum suggestions
    
    Returns:
        Sorted list of station name suggestions
        
    Example:
        >>> autocomplete_station("khan", station_list, limit=3)
        ['Khan Market', 'Khanpur']
    """
    results = fuzzy_search_station(query, choices, limit=limit, threshold=40)
    return [r["name"] for r in results]


def best_match_station(query: str, choices: List[str]) -> Optional[str]:
    """
    Find the single best matching station.
    
    Args:
        query: Search query
        choices: Station names to search
    
    Returns:
        Best matching station name, or None if no good match
        
    Example:
        >>> best_match_station("rajiv chok", station_list)
        'Rajiv Chowk'
    """
    results = fuzzy_search_station(query, choices, limit=1, threshold=60)
    return results[0]["name"] if results else None


def compare_similarity(query: str, choice: str, scorer: str = "WRatio") -> int:
    """
    Get similarity score between two strings.
    
    Args:
        query: First string
        choice: Second string
        scorer: Scoring algorithm
    
    Returns:
        Similarity score (0-100)
        
    Example:
        >>> compare_similarity("rajiv chowk", "Rajiv Chowk")
        100
    """
    scorer_map = {
        "WRatio": fuzz.WRatio,
        "Ratio": fuzz.ratio,
        "PartialRatio": fuzz.partial_ratio,
        "TokenSort": fuzz.token_sort_ratio,
        "TokenSet": fuzz.token_set_ratio,
    }
    
    scoring_func = scorer_map.get(scorer, fuzz.WRatio)
    return scoring_func(query, choice)


if __name__ == "__main__":
    # Quick test
    test_stations = [
        "Rajiv Chowk",
        "Khan Market",
        "Khanpur",
        "Connaught Place",
        "Central Secretariat",
        "New Delhi",
        "Old Delhi",
        "Chandni Chowk",
        "Delhi Gate",
    ]
    
    print("=" * 60)
    print("FUZZY SEARCH MODULE - TEST")
    print("=" * 60)
    
    # Test 1: Basic fuzzy search
    print("\nTest 1: Basic Fuzzy Search")
    print("-" * 60)
    results = fuzzy_search_station("rajeev chok", test_stations, limit=3)
    print("Query: 'rajeev chok'")
    for r in results:
        print("  - {} (Score: {})".format(r["name"], r["score"]))
    
    # Test 2: Autocomplete
    print("\nTest 2: Autocomplete")
    print("-" * 60)
    suggestions = autocomplete_station("khan", test_stations, limit=5)
    print("Query: 'khan'")
    print("Suggestions: {}".format(suggestions))
    
    # Test 3: Best match
    print("\nTest 3: Best Match")
    print("-" * 60)
    best = best_match_station("chandi chawk", test_stations)
    print("Query: 'chandi chawk'")
    print("Best match: {}".format(best))
    
    # Test 4: Similarity comparison
    print("\nTest 4: Similarity Scoring")
    print("-" * 60)
    queries = ["rajiv chowk", "rajeev chok", "Chowk Rajiv"]
    for q in queries:
        score = compare_similarity(q, "Rajiv Chowk")
        print("'{}' vs 'Rajiv Chowk': {}".format(q, score))
    
    # Test 5: Different scorers
    print("\nTest 5: Different Scorers")
    print("-" * 60)
    query = "delhi gate"
    scorers = ["WRatio", "TokenSort", "PartialRatio"]
    results_by_scorer = {}
    for scorer in scorers:
        results = fuzzy_search_with_scorer(
            query, 
            test_stations, 
            scorer=scorer, 
            limit=3
        )
        results_by_scorer[scorer] = results
        print("\nScorer: {}".format(scorer))
        for r in results:
            print("  - {} ({})".format(r["name"], r["score"]))
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
