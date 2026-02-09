from pathlib import Path
import csv
import argparse
import importlib.util
import sys
import re
import shutil

PROJECT_ROOT = Path(__file__).parent.resolve()
OUTPUT_MASTER = PROJECT_ROOT / "dmrc_master_stations.csv"
ACTIVE_STATIONS = PROJECT_ROOT / "dmrc_master_stations.csv"
ROUTES_DIR = PROJECT_ROOT / "routes"
BACKUP_SUFFIX = ".bak"

def import_from_path(path: Path, var_names):
    if not path.exists():
        return {}
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)  # type: ignore
    except Exception as e:
        print(f"Failed to import {path}: {e}")
        return {}
    result = {}
    for name in var_names:
        if hasattr(module, name):
            result[name] = getattr(module, name)
    return result

def load_metro_data():
    candidates = [PROJECT_ROOT / "main_enhanced.py", PROJECT_ROOT / "main.py"]
    for p in candidates:
        vars_found = import_from_path(p, ["METRO_DATA", "INTERCHANGES"])
        if "METRO_DATA" in vars_found:
            metro = vars_found["METRO_DATA"]
            interchanges = vars_found.get("INTERCHANGES", {})
            print(f"Loaded METRO_DATA from {p.name}")
            return metro, interchanges
    raise RuntimeError("Could not find METRO_DATA in main_enhanced.py or main.py in project root.")

def normalize_station_name(name: str) -> str:
    return re.sub(r"\s+", " ", name.strip())

def make_station_id(name: str, existing_ids:set):
    words = re.findall(r"[A-Za-z0-9]+", name)
    if not words:
        base = "STN"
    else:
        initials = "".join(w[0].upper() for w in words[:3])
        base = initials
    candidate = base
    i = 1
    while candidate in existing_ids:
        i += 1
        candidate = f"{base}{i}"
    existing_ids.add(candidate)
    return candidate

def write_master_csv(stations_map, output_path:Path):
    fieldnames = ["station_id","station_name","lines","interchange"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rec in stations_map.values():
            writer.writerow({
                "station_id": rec["station_id"],
                "station_name": rec["name"],
                "lines": ", ".join(rec["lines"]),
                "interchange": "Yes" if rec["is_interchange"] else "No"
            })
    print(f"Wrote master stations CSV: {output_path} ({len(list(stations_map))} stations)")

def write_routes_files(metro_data, routes_dir:Path):
    routes_dir.mkdir(exist_ok=True)
    for line_code, line_data in metro_data.items():
        stations = line_data.get("stations", [])
        fname = routes_dir / f"{line_code}_route.csv"
        with open(fname, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["line_code","line_name","station_order","station_name"])
            for idx, s in enumerate(stations, start=1):
                writer.writerow([line_code, line_data.get("name",""), idx, s])
        print(f"Wrote route file: {fname} ({len(stations)} stations)")

def backup_file(path:Path):
    if path.exists():
        b = path.with_suffix(path.suffix + BACKUP_SUFFIX)
        shutil.copy2(path, b)
        print(f"Backup created: {b}")

def main():
    parser = argparse.ArgumentParser(description="Generate DMRC master stations CSV and per-line route files.")
    parser.add_argument("--activate", action="store_true", help="Also copy master CSV to dmrc_stations_dataset.csv (backup created)")
    args = parser.parse_args()

    try:
        metro_data, interchanges = load_metro_data()
    except Exception as e:
        print("Error:", e)
        sys.exit(1)

    stations_map = {}
    existing_ids = set()

    for line_code, line in metro_data.items():
        stations = line.get("stations", [])
        for s in stations:
            name = normalize_station_name(s)
            key = name.lower()
            rec = stations_map.get(key)
            if not rec:
                rec = {"name": name, "lines": [], "is_interchange": False, "station_id": None}
            rec["lines"].append(line_code if line_code else str(line.get("name","")))
            stations_map[key] = rec

    inter_keys = {k.lower(): v for k,v in (interchanges.items() if isinstance(interchanges, dict) else [])}
    for key, rec in stations_map.items():
        if len(set(rec["lines"])) > 1:
            rec["is_interchange"] = True
        else:
            if key in inter_keys:
                rec["is_interchange"] = True
        stations_map[key] = rec

    for key, rec in stations_map.items():
        rec["station_id"] = make_station_id(rec["name"], existing_ids)

    write_master_csv(stations_map, OUTPUT_MASTER)
    write_routes_files(metro_data, ROUTES_DIR)

    if args.activate:
        if ACTIVE_STATIONS.exists():
            backup_file(ACTIVE_STATIONS)
        shutil.copy2(OUTPUT_MASTER, ACTIVE_STATIONS)
        print(f"Activated {ACTIVE_STATIONS} (backup created if existed).")

    print("Done. Restart your backend to pick up new station data if running.")

if __name__ == "__main__":
    main()
