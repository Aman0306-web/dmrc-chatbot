import csv
import difflib
from collections import defaultdict, deque

# ==========================================
# PART 1: VERIFIED DMRC MASTER DATASET
# ==========================================

# Ordered list of stations for every line (Correct as of 2026)
METRO_NETWORKS = {
    "Red Line": [
        "Shaheed Sthal", "Hindon River", "Arthala", "Mohan Nagar", "Shyam Park", 
        "Major Mohit Sharma Rajendra Nagar", "Raj Bagh", "Shaheed Nagar", "Dilshad Garden", 
        "Jhilmil", "Mansarovar Park", "Shahdara", "Welcome", "Seelampur", "Shastri Park", 
        "Kashmere Gate", "Tis Hazari", "Pul Bangash", "Pratap Nagar", "Shastri Nagar", 
        "Inderlok", "Kanhaiya Nagar", "Keshav Puram", "Netaji Subhash Place", 
        "Kohat Enclave", "Pitampura", "Rohini East", "Rohini West", "Rithala"
    ],
    "Yellow Line": [
        "Samaypur Badli", "Rohini Sector 18-19", "Haiderpur Badli Mor", "Jahangirpuri", 
        "Adarsh Nagar", "Azadpur", "Model Town", "GTB Nagar", "Vishwa Vidyalaya", 
        "Vidhan Sabha", "Civil Lines", "Kashmere Gate", "Chandni Chowk", "Chawri Bazar", 
        "New Delhi", "Rajiv Chowk", "Patel Chowk", "Central Secretariat", "Udyog Bhawan", 
        "Lok Kalyan Marg", "Jor Bagh", "Dilli Haat INA", "AIIMS", "Green Park", 
        "Hauz Khas", "Malviya Nagar", "Saket", "Qutab Minar", "Chhatarpur", "Sultanpur", 
        "Ghitorni", "Arjan Garh", "Guru Dronacharya", "Sikanderpur", "MG Road", 
        "IFFCO Chowk", "Millennium City Centre Gurugram"
    ],
    "Blue Line": [
        "Dwarka Sector 21", "Dwarka Sector 8", "Dwarka Sector 9", "Dwarka Sector 10", 
        "Dwarka Sector 11", "Dwarka Sector 12", "Dwarka Sector 13", "Dwarka Sector 14", 
        "Dwarka", "Dwarka Mor", "Nawada", "Uttam Nagar West", "Uttam Nagar East", 
        "Janakpuri West", "Janakpuri East", "Tilak Nagar", "Subhash Nagar", "Tagore Garden", 
        "Rajouri Garden", "Ramesh Nagar", "Moti Nagar", "Kirti Nagar", "Shadipur", 
        "Patel Nagar", "Rajendra Place", "Karol Bagh", "Jhandewalan", "Ramakrishna Ashram Marg", 
        "Rajiv Chowk", "Barakhamba Road", "Mandi House", "Supreme Court", "Indraprastha", 
        "Yamuna Bank", "Akshardham", "Mayur Vihar Phase-1", "Mayur Vihar Extension", 
        "New Ashok Nagar", "Noida Sector 15", "Noida Sector 16", "Noida Sector 18", 
        "Botanical Garden", "Golf Course", "Noida City Centre", "Noida Sector 34", 
        "Noida Sector 52", "Noida Sector 61", "Noida Sector 59", "Noida Sector 62", 
        "Noida Electronic City"
    ],
    "Blue Line Branch": [
        "Yamuna Bank", "Laxmi Nagar", "Nirman Vihar", "Preet Vihar", "Karkarduma", 
        "Anand Vihar ISBT", "Kaushambi", "Vaishali"
    ],
    "Green Line": [
        "Inderlok", "Ashok Park Main", "Punjabi Bagh", "Shivaji Park", "Madipur", 
        "Paschim Vihar East", "Paschim Vihar West", "Peeragarhi", "Udyog Nagar", 
        "Maharaja Surajmal Stadium", "Nangloi", "Nangloi Railway Station", "Rajdhani Park", 
        "Mundka", "Mundka Industrial Area", "Ghevra Metro Station", "Tikri Kalan", 
        "Tikri Border", "Pandit Shree Ram Sharma", "Bahadurgarh City", "Brigadier Hoshiar Singh"
    ],
    "Green Line Branch": [
        "Kirti Nagar", "Satguru Ram Singh Marg", "Ashok Park Main"
    ],
    "Violet Line": [
        "Kashmere Gate", "Lal Quila", "Jama Masjid", "Delhi Gate", "ITO", "Mandi House", 
        "Janpath", "Central Secretariat", "Khan Market", "Jawaharlal Nehru Stadium", 
        "Jangpura", "Lajpat Nagar", "Moolchand", "Kailash Colony", "Nehru Place", 
        "Kalkaji Mandir", "Govind Puri", "Harkesh Nagar Okhla", "Jasola Apollo", 
        "Sarita Vihar", "Mohan Estate", "Tughlakabad Station", "Badarpur Border", 
        "Sarai", "NHPC Chowk", "Mewala Maharajpur", "Sector 28 Faridabad", 
        "Badkal Mor", "Old Faridabad", "Neelam Chowk Ajronda", "Bata Chowk", 
        "Escorts Mujesar", "Sant Surdas (Sihi)", "Raja Nahar Singh"
    ],
    "Pink Line": [
        "Majlis Park", "Azadpur", "Shalimar Bagh", "Netaji Subhash Place", "Shakurpur", 
        "Punjabi Bagh West", "ESI - Basaidarapur", "Rajouri Garden", "Mayapuri", 
        "Naraina Vihar", "Delhi Cantt", "Durgabai Deshmukh South Campus", 
        "Sir M. Vishveshwaraya Moti Bagh", "Bhikaji Cama Place", "Sarojini Nagar", 
        "Dilli Haat INA", "South Extension", "Lajpat Nagar", "Vinobapuri", "Ashram", 
        "Sarai Kale Khan - Nizamuddin", "Mayur Vihar Phase-1", "Mayur Vihar Pocket I", 
        "Trilokpuri - Sanjay Lake", "East Vinod Nagar - Mayur Vihar-II", 
        "Mandawali - West Vinod Nagar", "IP Extension", "Anand Vihar ISBT", "Karkarduma", 
        "Karkarduma Court", "Krishna Nagar", "East Azad Nagar", "Welcome", "Jaffrabad", 
        "Maujpur - Babarpur", "Gokulpuri", "Johri Enclave", "Shiv Vihar"
    ],
    "Magenta Line": [
        "Janakpuri West", "Dabri Mor - Janakpuri South", "Dashrath Puri", "Palam", 
        "Sadar Bazaar Cantonment", "Terminal 1 IGI Airport", "Shankar Vihar", 
        "Vasant Vihar", "Munirka", "RK Puram", "IIT Delhi", "Hauz Khas", "Panchsheel Park", 
        "Chirag Delhi", "Greater Kailash", "Nehru Enclave", "Kalkaji Mandir", 
        "Okhla NSIC", "Sukhdev Vihar", "Jamia Millia Islamia", "Okhla Vihar", 
        "Jasola Vihar Shaheen Bagh", "Kalindi Kunj", "Okhla Bird Sanctuary", "Botanical Garden"
    ],
    "Grey Line": [
        "Dwarka", "Nangli", "Najafgarh", "Dhansa Bus Stand"
    ],
    "Airport Express": [
        "New Delhi", "Shivaji Stadium", "Dhaula Kuan", "Delhi Aerocity", "IGI Airport", 
        "Dwarka Sector 21", "Yashobhoomi Dwarka Sector 25"
    ]
}

def generate_dmrc_dataset():
    """
    Generates a list of dictionaries for all DMRC stations.
    Each dictionary represents a station on a specific line.
    """
    dataset = []
    
    # Prefix map for station codes
    PREFIX_MAP = {
        "Red Line": "RD", "Yellow Line": "YL", "Blue Line": "BL", 
        "Blue Line Branch": "BLB", "Green Line": "GR", "Green Line Branch": "GRB",
        "Violet Line": "VT", "Pink Line": "PK", "Magenta Line": "MG", 
        "Grey Line": "GY", "Airport Express": "AE"
    }

    # First pass: Identify all lines for each station to determine interchanges
    station_lines_map = {}
    for line, stations in METRO_NETWORKS.items():
        for station in stations:
            if station not in station_lines_map:
                station_lines_map[station] = set()
            station_lines_map[station].add(line)

    # Second pass: Build the dataset
    for line, stations in METRO_NETWORKS.items():
        for i, station_name in enumerate(stations):
            # Determine neighbors on the same line
            neighbors = []
            if i > 0:
                neighbors.append(stations[i-1])
            if i < len(stations) - 1:
                neighbors.append(stations[i+1])
            
            # Determine interchange info
            all_lines = station_lines_map[station_name]
            interchange_lines = list(all_lines - {line})
            is_interchange = len(interchange_lines) > 0
            
            # Generate Station Code
            prefix = PREFIX_MAP.get(line, "XX")
            code = f"{prefix}{i+1:02d}"
            
            record = {
                "name": station_name,
                "line": line,
                "code": code,
                "neighbors": neighbors,
                "interchange": is_interchange,
                "interchange_lines": interchange_lines
            }
            dataset.append(record)
            
    return dataset

# The Master Dataset Variable
STATION_DATASET = generate_dmrc_dataset()

# ==========================================
# PART 2: GRAPH BUILDER
# ==========================================

def build_metro_graph(dataset):
    """
    Constructs an adjacency graph for the Metro network.
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
            graph[station][neighbor] = 1
            
            # Ensure bidirectional connection immediately
            if neighbor not in graph:
                graph[neighbor] = {}
            graph[neighbor][station] = 1
            
    return dict(graph)

def get_station_line_map(dataset):
    """
    Creates a lookup dictionary: Station Name -> List of Lines
    """
    mapping = defaultdict(set)
    for record in dataset:
        mapping[record['name']].add(record['line'])
    
    # Convert sets to sorted lists for consistency
    return {k: sorted(list(v)) for k, v in mapping.items()}

# Initialize Global Graph and Mappings
METRO_GRAPH = build_metro_graph(STATION_DATASET)
STATION_LINE_LOOKUP = get_station_line_map(STATION_DATASET)

# ==========================================
# PART 4: HELPER FUNCTIONS & VALIDATION
# ==========================================

def normalize_station_name(name):
    """
    Cleans up user input: removes extra spaces, converts to Title Case.
    """
    if not isinstance(name, str):
        return ""
    return " ".join(name.strip().split()).title()

def validate_station(name):
    """
    Validates if a station exists in the graph.
    Supports case-insensitive matching and fuzzy matching for typos.
    """
    if not name:
        return False, None
        
    clean_name = normalize_station_name(name)
    
    # 1. Exact Match Check
    if clean_name in METRO_GRAPH:
        return True, clean_name
        
    # 2. Case-Insensitive Check
    stations_lower = {k.lower(): k for k in METRO_GRAPH.keys()}
    if clean_name.lower() in stations_lower:
        return True, stations_lower[clean_name.lower()]
        
    # 3. Fuzzy Match (Did you mean?)
    matches = difflib.get_close_matches(clean_name, METRO_GRAPH.keys(), n=1, cutoff=0.6)
    if matches:
        return False, matches[0] # Return the suggestion
        
    return False, None

def format_route_text(route_result):
    """
    Formats the route dictionary into a user-friendly string.
    """
    if "error" in route_result:
        return f"⚠️ {route_result['error']}"
        
    src = route_result['source']
    dst = route_result['destination']
    total = route_result['total_stations']
    changes = route_result['interchanges']
    steps = route_result['steps']
    
    lines = []
    lines.append(f"🚇 **Metro Route: {src} ➝ {dst}**")
    lines.append(f"⏱️  Total Stations: {total}")
    lines.append(f"🔀  Interchanges: {changes}")
    lines.append("-" * 40)
    
    for i, step in enumerate(steps):
        lines.append(f"**Step {i+1}:** Board {step['line']}")
        lines.append(f"   📍 From: {step['start']}")
        lines.append(f"   🏁 To:   {step['end']}")
        lines.append(f"   🚋 Ride: {step['stops']} stops")
        
        if i < len(steps) - 1:
            lines.append("\n   🔄 **CHANGE TRAIN** ⬇️\n")
            
    lines.append("-" * 40)
    lines.append("✅ End of Route")
    
    return "\n".join(lines)

# ==========================================
# PART 3: ROUTE FINDING LOGIC
# ==========================================

def find_shortest_path_bfs(start_node, end_node, graph=METRO_GRAPH):
    """
    Finds the shortest path between two stations using BFS.
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
    
    # If multiple lines connect, pick the first one
    return list(common_lines)[0]

def format_route_details(path):
    """
    Converts a list of stations into a step-by-step navigation guide.
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
    save_dataset_to_csv()
    run_tests()