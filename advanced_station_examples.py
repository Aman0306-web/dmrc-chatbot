"""
Advanced StationLoader Examples - Real Chatbot Use Cases
Shows practical examples of how to use StationLoader for the DMRC chatbot
"""

import sys
sys.path.insert(0, '.')

from station_loader import StationLoader

def main():
    loader = StationLoader("dmrc_stations_dataset.csv")
    
    print("=" * 70)
    print("ADVANCED STATIONLOADER EXAMPLES - CHATBOT USE CASES")
    print("=" * 70)
    
    # USE CASE 1: "Is Connaught Place an interchange?"
    print("\n[USE CASE 1] 'Is Connaught Place an interchange?'")
    print("-" * 70)
    station = loader.get_station("Connaught Place")
    if station:
        is_interchange = len(station['lines']) > 1
        print("Answer: {}".format("Yes" if is_interchange else "No"))
        print("Connaught Place station is on: {}".format(", ".join(station['lines'])))
        if is_interchange:
            print("You can interchange between {} and {} lines here".format(
                station['lines'][0], station['lines'][1]))
    
    # USE CASE 2: "How many stations are on the Yellow line?"
    print("\n[USE CASE 2] 'How many stations are on the Yellow line?'")
    print("-" * 70)
    yellow_stations = loader.get_line_stations("yellow")
    print("Answer: {} stations".format(len(yellow_stations)))
    print("Route: {} -> {}".format(yellow_stations[0], yellow_stations[-1]))
    print("Stations: {}".format(", ".join(yellow_stations[:5])) + " ... {} more".format(
        len(yellow_stations) - 5))
    
    # USE CASE 3: "Which stations are interchanges?"
    print("\n[USE CASE 3] 'Which stations are interchanges?'")
    print("-" * 70)
    interchanges = [s for s in loader.stations.values() if len(s['lines']) > 1]
    print("Answer: {} interchange stations found".format(len(interchanges)))
    for station in sorted(interchanges, key=lambda x: len(x['lines']), reverse=True)[:5]:
        print("  - {}: {} lines ({})".format(
            station['name'], 
            len(station['lines']),
            ", ".join(station['lines'])))
    
    # USE CASE 4: "What's the starting and ending station of Red line?"
    print("\n[USE CASE 4] 'What is the starting and ending station of Red line?'")
    print("-" * 70)
    red_stations = loader.get_line_stations("red")
    print("Answer:")
    print("  Start: {}".format(red_stations[0]))
    print("  End:   {}".format(red_stations[-1]))
    print("  Total: {} stations on Red line".format(len(red_stations)))
    
    # USE CASE 5: "Show me all the Blue line stations"
    print("\n[USE CASE 5] 'Show me all the Blue line stations'")
    print("-" * 70)
    blue_stations = loader.get_line_stations("blue")
    print("Blue Line Route ({} stations):".format(len(blue_stations)))
    for i, station in enumerate(blue_stations, 1):
        print("  {}. {}".format(i, station))
    
    # USE CASE 6: Search with fuzzy matching
    print("\n[USE CASE 6] Search 'new' (fuzzy matching)")
    print("-" * 70)
    results = loader.search("new")
    print("Answer: Found {} station(s)".format(len(results)))
    for station in results:
        print("  - {} (on {} line{})".format(
            station['name'],
            len(station['lines']),
            "s" if len(station['lines']) > 1 else ""))
    
    # USE CASE 7: "Can I go from Terminal 1 to Chandni Chowk?"
    print("\n[USE CASE 7] 'Can I go from Terminal 1 to Chandni Chowk?'")
    print("-" * 70)
    t1 = loader.get_station("Terminal 1 IGI Airport")
    chandni = loader.get_station("Chandni Chowk")
    if t1 and chandni:
        print("Terminal 1 IGI Airport lines: {}".format(", ".join(t1['lines'])))
        print("Chandni Chowk lines: {}".format(", ".join(chandni['lines'])))
        common = set(t1['lines']) & set(chandni['lines'])
        if common:
            print("Answer: YES, you can travel via the {} line".format(
                list(common)[0].upper()))
        else:
            print("Answer: NO direct line, you need to interchange")
    
    # USE CASE 8: List all available lines
    print("\n[USE CASE 8] 'What are all the metro lines?'")
    print("-" * 70)
    all_lines = loader.list_all_lines()
    print("Answer: {} metro lines available:".format(len(all_lines)))
    for line in all_lines:
        station_count = len(loader.get_line_stations(line))
        print("  - {} Line: {} stations".format(line.upper(), station_count))
    
    # USE CASE 9: Station not found (graceful handling)
    print("\n[USE CASE 9] 'Information about Unknown Station'")
    print("-" * 70)
    unknown = loader.get_station("XYZ Station That Does Not Exist")
    if unknown:
        print("Station found: {}".format(unknown['name']))
    else:
        print("Answer: I could not find 'XYZ Station That Does Not Exist' in our database")
        print("Did you mean one of these?")
        suggestions = loader.search("Unknown Station")[:3]
        if suggestions:
            for s in suggestions:
                print("  - {}".format(s['name']))
        else:
            print("Try searching with a different name")
    
    # USE CASE 10: "Stations on multiple lines" analysis
    print("\n[USE CASE 10] 'Which stations connect the most metro lines?'")
    print("-" * 70)
    top_stations = sorted(
        [s for s in loader.stations.values() if len(s['lines']) > 1],
        key=lambda x: len(x['lines']),
        reverse=True
    )[:5]
    print("Answer: Top 5 busiest interchange stations:")
    for i, station in enumerate(top_stations, 1):
        print("  {}. {} - connects {} lines: {}".format(
            i,
            station['name'],
            len(station['lines']),
            ", ".join([l.upper() for l in station['lines']])))
    
    print("\n" + "=" * 70)
    print("ALL USE CASES DEMONSTRATED")
    print("=" * 70)
    print("\nNote: Coordinates and graph connectivity features are available")
    print("      if you update dmrc_stations_dataset.csv with lat/lon values")

if __name__ == "__main__":
    main()
