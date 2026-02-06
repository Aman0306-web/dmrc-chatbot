"""
Routing utilities: BFS for fewest-stations, Dijkstra for shortest-distance.
Uses weights in station graph for distance calculations.
"""
import heapq
from collections import deque
from typing import Dict, List, Tuple, Optional

def bfs_shortest_path(graph: Dict[str, Dict], start: str, goal: str) -> Optional[List[str]]:
    """
    Breadth-First Search to find path with fewest stations.
    
    Args:
        graph: Adjacency list {station: {neighbor: distance_km, ...}, ...}
        start: Starting station name
        goal: Destination station name
    
    Returns:
        List of station names from start to goal, or None if no path exists
    
    Time Complexity: O(V + E) where V=stations, E=connections
    Space Complexity: O(V)
    """
    if start == goal:
        return [start]
    
    if start not in graph or goal not in graph:
        return None
    
    visited = set([start])
    queue = deque([[start]])
    
    while queue:
        path = queue.popleft()
        node = path[-1]
        
        for neighbor in graph.get(node, {}):
            if neighbor in visited:
                continue
            
            new_path = path + [neighbor]
            
            if neighbor == goal:
                return new_path
            
            visited.add(neighbor)
            queue.append(new_path)
    
    return None


def dijkstra(graph: Dict[str, Dict], start: str, goal: str) -> Optional[Tuple[float, List[str]]]:
    """
    Dijkstra's algorithm to find shortest distance path.
    Uses edge weights (distances in km) from the graph.
    
    Args:
        graph: Adjacency list {station: {neighbor: distance_km, ...}, ...}
        start: Starting station name
        goal: Destination station name
    
    Returns:
        Tuple of (total_distance_km, [path_stations]) or None if no path exists
    
    Time Complexity: O((V + E) log V) with binary heap
    Space Complexity: O(V)
    """
    if start == goal:
        return 0.0, [start]
    
    if start not in graph or goal not in graph:
        return None
    
    # Priority queue: (distance, current_node, path)
    priority_queue = [(0.0, start, [start])]
    seen = {}
    
    while priority_queue:
        distance, node, path = heapq.heappop(priority_queue)
        
        # Skip if we've already found better path to this node
        if node in seen and seen[node] <= distance:
            continue
        
        seen[node] = distance
        
        # Goal reached
        if node == goal:
            return distance, path
        
        # Explore neighbors
        for neighbor, weight in graph.get(node, {}).items():
            # Use weight if available, else default to 1.0
            edge_distance = weight if weight else 1.0
            new_distance = distance + edge_distance
            
            # Only add if we haven't seen this node or found a better path
            if neighbor not in seen or new_distance < seen.get(neighbor, float('inf')):
                heapq.heappush(priority_queue, (new_distance, neighbor, path + [neighbor]))
    
    return None


def get_all_paths_limited(graph: Dict[str, Dict], start: str, goal: str, 
                          max_length: int = 5) -> List[List[str]]:
    """
    Find all paths from start to goal up to a maximum length.
    Useful for showing alternative routes.
    
    Args:
        graph: Adjacency list
        start: Starting station
        goal: Destination station
        max_length: Maximum number of stations in path
    
    Returns:
        List of paths, each path is a list of station names
    """
    if start not in graph or goal not in graph:
        return []
    
    paths = []
    
    def dfs(node: str, path: List[str], visited: set):
        if len(path) > max_length:
            return
        
        if node == goal:
            paths.append(path[:])
            return
        
        for neighbor in graph.get(node, {}):
            if neighbor not in visited:
                visited.add(neighbor)
                path.append(neighbor)
                dfs(neighbor, path, visited)
                path.pop()
                visited.remove(neighbor)
    
    visited = {start}
    dfs(start, [start], visited)
    
    return paths


def find_nearest_common_station(graph: Dict[str, Dict], station_a: str, 
                                station_b: str) -> Optional[str]:
    """
    Find the nearest station that both stations can reach (interchange point).
    
    Args:
        graph: Adjacency list
        station_a: First station
        station_b: Second station
    
    Returns:
        Name of nearest common station, or None if not reachable
    """
    if station_a not in graph or station_b not in graph:
        return None
    
    # BFS from both directions to find common stations
    visited_a = {station_a}
    visited_b = {station_b}
    queue_a = deque([(station_a, 0)])
    queue_b = deque([(station_b, 0)])
    level_a = 0
    level_b = 0
    
    while queue_a or queue_b:
        if queue_a:
            next_queue_a = deque()
            level_a += 1
            while queue_a:
                node, _ = queue_a.popleft()
                for neighbor in graph.get(node, {}):
                    if neighbor in visited_b:
                        return neighbor
                    if neighbor not in visited_a:
                        visited_a.add(neighbor)
                        next_queue_a.append((neighbor, level_a))
            queue_a = next_queue_a
        
        if queue_b:
            next_queue_b = deque()
            level_b += 1
            while queue_b:
                node, _ = queue_b.popleft()
                for neighbor in graph.get(node, {}):
                    if neighbor in visited_a:
                        return neighbor
                    if neighbor not in visited_b:
                        visited_b.add(neighbor)
                        next_queue_b.append((neighbor, level_b))
            queue_b = next_queue_b
    
    return None


def get_connected_component(graph: Dict[str, Dict], start: str) -> set:
    """
    Find all stations reachable from start station.
    
    Args:
        graph: Adjacency list
        start: Starting station
    
    Returns:
        Set of all reachable station names
    """
    if start not in graph:
        return set()
    
    visited = {start}
    queue = deque([start])
    
    while queue:
        node = queue.popleft()
        for neighbor in graph.get(node, {}):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    return visited


def is_reachable(graph: Dict[str, Dict], start: str, goal: str) -> bool:
    """
    Check if goal station is reachable from start station.
    
    Args:
        graph: Adjacency list
        start: Starting station
        goal: Destination station
    
    Returns:
        True if reachable, False otherwise
    """
    return goal in get_connected_component(graph, start)


if __name__ == "__main__":
    # Example usage
    test_graph = {
        "Station A": {"Station B": 1.5, "Station C": 2.0},
        "Station B": {"Station A": 1.5, "Station D": 1.2},
        "Station C": {"Station A": 2.0, "Station E": 1.8},
        "Station D": {"Station B": 1.2, "Station E": 0.9},
        "Station E": {"Station C": 1.8, "Station D": 0.9},
    }
    
    print("Testing Routing Algorithms")
    print("=" * 50)
    
    # Test BFS
    bfs_path = bfs_shortest_path(test_graph, "Station A", "Station E")
    print(f"BFS (fewest stations): {' -> '.join(bfs_path)}")
    
    # Test Dijkstra
    dijkstra_res = dijkstra(test_graph, "Station A", "Station E")
    if dijkstra_res:
        dist, path = dijkstra_res
        print(f"Dijkstra (shortest distance): {' -> '.join(path)}")
        print(f"Total distance: {dist:.1f} km")
    
    # Test alternative paths
    all_paths = get_all_paths_limited(test_graph, "Station A", "Station E", max_length=4)
    print(f"\nAlternative routes: {len(all_paths)} found")
    for i, path in enumerate(all_paths, 1):
        print(f"  Route {i}: {' -> '.join(path)}")
    
    # Test nearest common station
    common = find_nearest_common_station(test_graph, "Station A", "Station C")
    print(f"\nNearest interchange (A & C): {common}")
    
    # Test connectivity
    connected = get_connected_component(test_graph, "Station A")
    print(f"\nReachable from Station A: {connected}")
