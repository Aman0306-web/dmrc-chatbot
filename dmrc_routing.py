from collections import deque
from dmrc_graph import METRO_GRAPH, STATION_LINE_LOOKUP

# ==========================================
# PART 3: ROUTE FINDING LOGIC
# ==========================================

def find_shortest_path_bfs(start_node, end_node, graph=METRO_GRAPH):
    """
    Finds the shortest path between two stations using BFS.
    Returns a list of station names (the path).
    """
    # Basic Validation
    if start_node not in graph:
        return None # Start station invalid
    if end_node not in graph:
        return None # End station invalid

    if start_node == end_node:
        return [start_node]

    # BFS Initialization
    queue = deque([[start_node]])
    visited = {start_node}

    while queue:
        path = queue.popleft()
        node = path[-1]

        if node == end_node:
            return path

        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                new_path = list(path)
                new_path.append(neighbor)
                queue.append(new_path)
    
    return None

def get_connecting_line(station1, station2):
    """
    Identifies which line connects two adjacent stations.
    """
    lines1 = set(STATION_LINE_LOOKUP.get(station1, []))
    lines2 = set(STATION_LINE_LOOKUP.get(station2, []))
    
    common_lines = lines1.intersection(lines2)
    
    if not common_lines:
        return "Unknown Line"
    
    # If multiple lines connect, pick the first one (e.g., parallel lines)
    return list(common_lines)[0]

def format_route_details(path):
    """
    Converts a list of stations into a step-by-step navigation guide.
    Detects where line changes occur.
    """
    if not path or len(path) < 2:
        return []

    route_steps = []
    start_station = path[0]
    current_line = get_connecting_line(path[0], path[1])
    
    # Iterate through the path to find line changes
    for i in range(1, len(path) - 1):
        next_line = get_connecting_line(path[i], path[i+1])
        
        # If line changes, record the segment
        if next_line != current_line:
            route_steps.append({
                "start": start_station,
                "end": path[i],
                "line": current_line,
                "stops": path.index(path[i]) - path.index(start_station)
            })
            # Update for next segment
            start_station = path[i]
            current_line = next_line
            
    # Add the final segment
    route_steps.append({
        "start": start_station,
        "end": path[-1],
        "line": current_line,
        "stops": len(path) - 1 - path.index(start_station)
    })
    
    return route_steps

def find_route(source, destination):
    """
    Main entry point for route finding.
    Returns a dictionary with path details.
    """
    path = find_shortest_path_bfs(source, destination)
    
    if not path:
        return {"error": f"No route found between {source} and {destination}"}
        
    steps = format_route_details(path)
    
    return {
        "source": source,
        "destination": destination,
        "total_stations": len(path),
        "interchanges": len(steps) - 1,
        "path": path,
        "steps": steps
    }

if __name__ == "__main__":
    # Test Case
    src = "Rajiv Chowk"
    dst = "Noida City Centre"
    
    print(f"🚀 Finding route from {src} to {dst}...\n")
    result = find_route(src, dst)
    
    if "error" in result:
        print(result["error"])
    else:
        print(f"Total Stations: {result['total_stations']}")
        print(f"Interchanges: {result['interchanges']}")
        print("-" * 40)
        for i, step in enumerate(result['steps']):
            print(f"{i+1}. Start at {step['start']} ({step['line']})")
            print(f"   ↓ Travel {step['stops']} stops")
            print(f"   Reach {step['end']}")
            if i < len(result['steps']) - 1:
                print("   🔄 CHANGE LINE")
        print("-" * 40)