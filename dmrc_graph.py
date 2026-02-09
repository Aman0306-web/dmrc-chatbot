from collections import defaultdict
from dmrc_dataset import STATION_DATASET

# ==========================================
# PART 2: GRAPH BUILDER
# ==========================================

def build_metro_graph(dataset):
    """
    Constructs an adjacency graph for the Metro network.
    
    Structure:
    {
        "Station Name": {
            "Neighbor Name": weight (1),
            ...
        },
        ...
    }
    
    Interchanges are handled implicitly: Since 'Rajiv Chowk' appears in both
    Yellow and Blue line records, the single node 'Rajiv Chowk' will accumulate 
    neighbors from both lines.
    """
    graph = defaultdict(dict)
    
    for record in dataset:
        station = record['name']
        
        # Ensure the station node exists in the graph
        if station not in graph:
            graph[station] = {}
            
        # Add edges for all neighbors on this line
        for neighbor in record['neighbors']:
            # Weight = 1 (representing 1 station hop)
            # This ensures BFS/Dijkstra finds the path with fewest stops
            graph[station][neighbor] = 1
            
            # Ensure bidirectional connection immediately
            if neighbor not in graph:
                graph[neighbor] = {}
            graph[neighbor][station] = 1
            
    return dict(graph)

def get_station_line_map(dataset):
    """
    Creates a lookup dictionary: Station Name -> List of Lines
    Useful for displaying which lines a station belongs to.
    """
    mapping = defaultdict(set)
    for record in dataset:
        mapping[record['name']].add(record['line'])
    
    # Convert sets to sorted lists for consistency
    return {k: sorted(list(v)) for k, v in mapping.items()}

# Initialize Global Graph and Mappings
METRO_GRAPH = build_metro_graph(STATION_DATASET)
STATION_LINE_LOOKUP = get_station_line_map(STATION_DATASET)

if __name__ == "__main__":
    # Validation / Debugging
    print(f"✅ Graph built successfully with {len(METRO_GRAPH)} stations.")
    
    test_station = "Rajiv Chowk"
    if test_station in METRO_GRAPH:
        print(f"\n🔍 Inspection for {test_station}:")
        print(f"   Lines: {STATION_LINE_LOOKUP[test_station]}")
        print(f"   Direct Connections: {list(METRO_GRAPH[test_station].keys())}")