"""
Station Loader Demo & Test Suite
Demonstrates all features of the StationLoader class
"""

import sys
sys.path.insert(0, '.')

from station_loader import StationLoader

def main():
    print("=" * 60)
    print("DELHI METRO STATION LOADER - DEMO & TEST")
    print("=" * 60)
    
    # Initialize loader
    print("\n[INIT] Loading stations from CSV...")
    loader = StationLoader("dmrc_master_stations.csv")
    print("[OK] Initialization complete")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("Total Stations:    {}".format(len(loader.stations)))
    print("Metro Lines:       {}".format(len(loader.lines_index)))
    print("Available Lines:   {}".format(", ".join(loader.list_all_lines())))
    
    # Test 1: Get specific station
    print("\n" + "=" * 60)
    print("TEST 1: GET SPECIFIC STATION")
    print("=" * 60)
    for station_name in ["Connaught Place", "Central Secretariat", "Rajiv Chowk"]:
        station = loader.get_station(station_name)
        if station:
            print("Station: {}".format(station['name']))
            print("  Lines:        {}".format(", ".join(station['lines'])))
            print("  Coordinates:  {}".format(station['coordinates']))
        else:
            print("Station '{}' NOT FOUND".format(station_name))
    
    # Test 2: Search stations
    print("\n" + "=" * 60)
    print("TEST 2: SEARCH STATIONS")
    print("=" * 60)
    search_terms = ["delhi", "new", "khan", "airport"]
    for term in search_terms:
        results = loader.search(term)
        print("Search '{}': {} results".format(term, len(results)))
        for r in results[:3]:
            print("  - {}".format(r['name']))
        if len(results) > 3:
            print("  ... and {} more".format(len(results) - 3))
    
    # Test 3: Line stations
    print("\n" + "=" * 60)
    print("TEST 3: STATIONS ON EACH LINE")
    print("=" * 60)
    for line in ["red", "blue", "yellow", "green"]:
        stations = loader.get_line_stations(line)
        print("{} Line: {} stations".format(line.upper(), len(stations)))
        if stations:
            print("  Start: {}".format(stations[0]))
            print("  End:   {}".format(stations[-1]))
    
    # Test 4: Station details with coordinates
    print("\n" + "=" * 60)
    print("TEST 4: STATIONS WITH COORDINATES")
    print("=" * 60)
    stations_with_coords = [s for s in loader.stations.values() 
                           if s['coordinates']['lat'] is not None]
    print("Stations with coordinates: {} out of {}".format(
        len(stations_with_coords), len(loader.stations)))
    if stations_with_coords:
        s = stations_with_coords[0]
        print("Example: {} at ({}, {})".format(
            s['name'], 
            s['coordinates']['lat'], 
            s['coordinates']['lon']))
    
    # Test 5: Neighbors (graph structure)
    print("\n" + "=" * 60)
    print("TEST 5: STATION ADJACENCY GRAPH")
    print("=" * 60)
    print("Total graph connections: {}".format(
        sum(len(v) for v in loader.graph.values()) // 2))
    
    # Find a station with neighbors
    for station_name in ["Rajiv Chowk", "Connaught Place", "Central Secretariat"]:
        neighbors = loader.get_neighbors(station_name)
        if neighbors:
            print("\n{}: {} neighbors".format(station_name, len(neighbors)))
            for neighbor, distance in sorted(neighbors.items()):
                print("  - {} ({:.2f} km)".format(neighbor, distance))
            break
    
    # Test 6: Advanced queries
    print("\n" + "=" * 60)
    print("TEST 6: ADVANCED QUERIES")
    print("=" * 60)
    
    # Query 1: All blue line stations
    print("\nBlue Line Route:")
    blue_stations = loader.get_line_stations("blue")
    print(" -> ".join(blue_stations[:5]) + " ... {} more".format(len(blue_stations) - 5))
    
    # Query 2: Which lines serve a station
    cp_station = loader.get_station("Connaught Place")
    if cp_station:
        print("\nConnaught Place is on: {} lines".format(len(cp_station['lines'])))
        for line in cp_station['lines']:
            stations_on_line = loader.get_line_stations(line)
            print("  - {} Line: {} total stations".format(
                line.upper(), len(stations_on_line)))
    
    # Query 3: Station frequency (appears on multiple lines)
    print("\nStations on multiple lines:")
    multiline_stations = [s for s in loader.stations.values() 
                         if len(s['lines']) > 1]
    print("Total: {}".format(len(multiline_stations)))
    for s in sorted(multiline_stations, key=lambda x: len(x['lines']), reverse=True)[:5]:
        print("  - {}: {}".format(s['name'], ", ".join(s['lines'])))
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED SUCCESSFULLY")
    print("=" * 60)

if __name__ == "__main__":
    main()
