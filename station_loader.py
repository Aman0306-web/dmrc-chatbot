"""
Station loader: read CSVs, validate and normalize stations,
build line -> ordered station lists and an adjacency graph.
"""
import csv
import os
import math
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

def haversine_km(a_lat, a_lon, b_lat, b_lon):
    R = 6371.0
    lat1, lon1 = math.radians(a_lat), math.radians(a_lon)
    lat2, lon2 = math.radians(b_lat), math.radians(b_lon)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

class StationLoader:
    def __init__(self, stations_csv="dmrc_stations_dataset.csv", stations_meta_csv=None, lines_routes_csv=None):
        self.stations_csv = stations_csv
        self.stations_meta_csv = stations_meta_csv
        self.lines_routes_csv = lines_routes_csv
        self.stations: Dict[str, Dict] = {}
        self.lines_index = defaultdict(list)  # line -> list of station names (as seen)
        self.graph = defaultdict(dict)  # adjacency: {station: {neighbor: distance_km}}
        self.load()

    def _normalize(self, name: str) -> str:
        return name.strip()

    def load(self):
        if not os.path.exists(self.stations_csv):
            raise FileNotFoundError(f"Stations file not found: {self.stations_csv}")
        # Primary CSV parser
        with open(self.stations_csv, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = self._normalize(row.get('Station', '') or row.get('station_name', ''))
                line = (row.get('Line') or row.get('lines') or '').strip()
                lat = row.get('Latitude') or row.get('latitude') or row.get('Lat') or ''
                lon = row.get('Longitude') or row.get('longitude') or row.get('Lon') or ''
                try:
                    latv = float(lat) if lat not in (None, '', 'None') else None
                    lonv = float(lon) if lon not in (None, '', 'None') else None
                except ValueError:
                    latv, lonv = None, None

                if not name:
                    continue
                if name not in self.stations:
                    self.stations[name] = {
                        "name": name,
                        "lines": set(),
                        "coordinates": {"lat": latv, "lon": lonv},
                        "meta": {}
                    }
                if line:
                    for part in [p.strip() for p in line.split(',') if p.strip()]:
                        canon = self._canonical_line(part)
                        self.stations[name]["lines"].add(canon)
                        self.lines_index[canon].append(name)

        # Optional meta CSV merge
        if self.stations_meta_csv and os.path.exists(self.stations_meta_csv):
            with open(self.stations_meta_csv, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    sname = row.get('station_name') or row.get('Station') or ''
                    sname = self._normalize(sname)
                    if not sname:
                        continue
                    if sname not in self.stations:
                        self.stations[sname] = {
                            "name": sname,
                            "lines": set(),
                            "coordinates": {"lat": None, "lon": None},
                            "meta": {}
                        }
                    if 'lines' in row and row['lines']:
                        for part in [p.strip() for p in row['lines'].split(',') if p.strip()]:
                            canon = self._canonical_line(part)
                            self.stations[sname]["lines"].add(canon)
                            self.lines_index[canon].append(sname)
                    self.stations[sname]["meta"].update(row)

        # If explicit ordered lines file exists, load it to ensure accurate adjacency
        if self.lines_routes_csv and os.path.exists(self.lines_routes_csv):
            self._load_lines_routes(self.lines_routes_csv)

        # Normalize sets to lists
        for s in self.stations.values():
            s['lines'] = sorted(list(s['lines']))
        # Build graph
        self._build_graph()

    def _canonical_line(self, raw: str) -> str:
        rn = raw.lower().replace('line', '').strip()
        rn = rn.replace('branch', '').strip()
        return rn

    def _load_lines_routes(self, path: str):
        # expected columns: line,sequence,station_name
        # builds lines_index as ordered lists if present
        ordered_by_line = defaultdict(list)
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                line = row.get('line') or row.get('Line') or ''
                seq = row.get('sequence') or row.get('seq') or ''
                station = row.get('station_name') or row.get('Station') or ''
                if not line or not station:
                    continue
                try:
                    seq_i = int(seq)
                except Exception:
                    seq_i = 0
                ordered_by_line[self._canonical_line(line)].append((seq_i, station.strip()))
        for line, items in ordered_by_line.items():
            items.sort()
            self.lines_index[line] = [s for _, s in items]

    def _build_graph(self):
        for line, stations in self.lines_index.items():
            seen = set()
            ordered = [s for s in stations if not (s in seen or seen.add(s))]
            coords_count = sum(1 for s in ordered if self._has_coords(s))
            if len(ordered) >= 2 and coords_count >= max(2, len(ordered)//3):
                for a, b in zip(ordered, ordered[1:]):
                    self._add_edge(a, b)
            else:
                for s in ordered:
                    if not self._has_coords(s):
                        continue
                    distances = []
                    for t in ordered:
                        if s == t or not self._has_coords(t):
                            continue
                        d = haversine_km(self.stations[s]['coordinates']['lat'],
                                         self.stations[s]['coordinates']['lon'],
                                         self.stations[t]['coordinates']['lat'],
                                         self.stations[t]['coordinates']['lon'])
                        distances.append((d, t))
                    distances.sort()
                    for _, t in distances[:2]:
                        self._add_edge(s, t)

    def _has_coords(self, name: str) -> bool:
        c = self.stations.get(name, {}).get('coordinates', {})
        return c.get('lat') is not None and c.get('lon') is not None

    def _add_edge(self, a: str, b: str):
        if a not in self.stations or b not in self.stations:
            return
        if self._has_coords(a) and self._has_coords(b):
            d = haversine_km(self.stations[a]['coordinates']['lat'],
                             self.stations[a]['coordinates']['lon'],
                             self.stations[b]['coordinates']['lat'],
                             self.stations[b]['coordinates']['lon'])
        else:
            d = 1.0
        self.graph[a][b] = d
        self.graph[b][a] = d

    def get_station(self, name: str) -> Optional[Dict]:
        return self.stations.get(self._normalize(name))

    def search(self, query: str):
        q = query.lower()
        return [s for s in self.stations.values() if q in s['name'].lower()]

    def nearby(self, lat: float, lon: float, radius_km: float = 1.0):
        results = []
        for s in self.stations.values():
            c = s['coordinates']
            if c.get('lat') is None or c.get('lon') is None:
                continue
            d = haversine_km(lat, lon, c['lat'], c['lon'])
            if d <= radius_km:
                results.append((d, s))
        results.sort(key=lambda x: x[0])
        return results

    def get_line_stations(self, line: str) -> List[str]:
        """Get all stations on a specific line in order"""
        canonical = self._canonical_line(line)
        return self.lines_index.get(canonical, [])

    def get_distance(self, station1: str, station2: str) -> Optional[float]:
        """Get distance between two adjacent stations"""
        s1 = self._normalize(station1)
        s2 = self._normalize(station2)
        return self.graph.get(s1, {}).get(s2)

    def get_neighbors(self, station: str) -> Dict[str, float]:
        """Get all adjacent stations and distances"""
        s = self._normalize(station)
        return self.graph.get(s, {})

    def list_all_lines(self) -> List[str]:
        """Get all available metro lines"""
        return sorted(list(self.lines_index.keys()))
