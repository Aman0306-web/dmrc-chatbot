#!/usr/bin/env python3
"""
add_or_merge_stations.py

Merge/expand DMRC stations CSV into your project safely.

Features:
- Reads existing project file: dmrc_stations_dataset.csv (if exists)
- Reads a source file provided by --source (example: full_stations.csv) OR falls back to dmrc_stations_dataset_expanded.csv if present
- Normalizes station names, lines, interchange flag
- Generates unique station_id when missing (based on initials + number)
- Deduplicates by station_name (case-insensitive)
- Writes merged output to dmrc_stations_dataset_full.csv
- Optionally overwrites the active dmrc_stations_dataset.csv with --activate (creates backup)
- Prints a summary of additions/changes

Usage:
    python add_or_merge_stations.py --source path/to/full_stations.csv --activate
    python add_or_merge_stations.py                # uses dmrc_chatbot..._expanded or existing files

Notes:
- Provide an authoritative source CSV if you want to load the full DMRC list.
- Expected CSV format:
    station_id,station_name,lines,interchange
- interchange should be "Yes"/"No" (case-insensitive). Lines can be "Blue, Yellow"
"""

import csv
import argparse
import os
from pathlib import Path
import shutil
import re

PROJECT_ROOT = Path(__file__).parent.resolve()
ACTIVE_FILENAME = PROJECT_ROOT / "dmrc_stations_dataset.csv"
EXPANDED_FALLBACK = PROJECT_ROOT / "dmrc_stations_dataset_expanded.csv"
OUTPUT_FULL = PROJECT_ROOT / "dmrc_stations_dataset_full.csv"
BACKUP_SUFFIX = ".bak"


def normalize_name(name: str) -> str:
    return re.sub(r'\s+', ' ', name.strip())


def normalize_lines(lines_field: str) -> str:
    if not lines_field:
        return ""
    parts = [p.strip().title() for p in re.split(r'[;,/]', lines_field) if p.strip()]
    final = []
    for p in parts:
        for sub in p.split(","):
            s = sub.strip()
            if s and s not in final:
                final.append(s)
    return ", ".join(final)


def normalize_interchange(val: str) -> str:
    if not val:
        return "No"
    v = val.strip().lower()
    if v in ("yes", "y", "true", "1"):
        return "Yes"
    return "No"


def read_csv(path: Path):
    rows = []
    if not path.exists():
        return rows
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({k: (v if v is not None else "") for k, v in r.items()})
    return rows


def write_csv(path: Path, rows, fieldnames):
    with open(path, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def generate_station_id(name: str, existing_ids: set):
    words = re.findall(r"[A-Za-z0-9]+", name)
    if not words:
        base = "STN"
    else:
        initials = "".join(w[0].upper() for w in words[:3])
        base = initials
    candidate = base
    suffix = 1
    while candidate in existing_ids:
        candidate = f"{base}{suffix}"
        suffix += 1
    existing_ids.add(candidate)
    return candidate


def merge_stations(existing_rows, source_rows):
    merged = {}
    existing_ids = set()
    for r in existing_rows:
        name = normalize_name(r.get("station_name", ""))
        key = name.lower()
        station_id = (r.get("station_id") or "").strip()
        if station_id:
            existing_ids.add(station_id)
        merged[key] = {
            "station_id": station_id,
            "station_name": name,
            "lines": normalize_lines(r.get("lines", "")),
            "interchange": normalize_interchange(r.get("interchange", ""))
        }

    added = 0
    updated = 0
    for r in source_rows:
        name_raw = r.get("station_name") or r.get("name") or ""
        name = normalize_name(name_raw)
        if not name:
            continue
        key = name.lower()
        src_lines = normalize_lines(r.get("lines", ""))
        src_inter = normalize_interchange(r.get("interchange", ""))

        if key in merged:
            existing = merged[key]
            combined_lines = []
            for part in (existing["lines"] + ", " + src_lines).split(","):
                p = part.strip()
                if p and p not in combined_lines:
                    combined_lines.append(p)
            new_lines = ", ".join([c for c in combined_lines if c])
            new_inter = "Yes" if (existing["interchange"]=="Yes" or src_inter=="Yes") else "No"
            if new_lines != existing["lines"] or new_inter != existing["interchange"]:
                existing["lines"] = new_lines
                existing["interchange"] = new_inter
                merged[key] = existing
                updated += 1
        else:
            merged[key] = {
                "station_id": (r.get("station_id") or "").strip(),
                "station_name": name,
                "lines": src_lines,
                "interchange": src_inter
            }
            if not merged[key]["station_id"]:
                pass
            else:
                existing_ids.add(merged[key]["station_id"])
            added += 1

    for key, rec in merged.items():
        if not rec.get("station_id"):
            rec["station_id"] = generate_station_id(rec["station_name"], existing_ids)
            merged[key] = rec

    rows_out = []
    for key in sorted(merged.keys(), key=lambda k: merged[k]["station_name"].lower()):
        rec = merged[key]
        rows_out.append({
            "station_id": rec["station_id"],
            "station_name": rec["station_name"],
            "lines": rec["lines"],
            "interchange": rec["interchange"]
        })

    return rows_out, added, updated


def backup_file(path: Path):
    if path.exists():
        b = path.with_suffix(path.suffix + BACKUP_SUFFIX)
        shutil.copy2(path, b)
        print(f"Backup created: {b}")


def main():
    parser = argparse.ArgumentParser(description="Merge/expand DMRC stations CSV into project.")
    parser.add_argument("--source", "-s", type=str, help="Source CSV with full station list to merge (station_id,station_name,lines,interchange)")
    parser.add_argument("--activate", action="store_true", help="Overwrite project's dmrc_stations_dataset.csv with merged file (creates backup)")
    parser.add_argument("--output", type=str, default=str(OUTPUT_FULL), help="Output full merged CSV filename")
    args = parser.parse_args()

    existing = read_csv(ACTIVE_FILENAME) if ACTIVE_FILENAME.exists() else []
    if existing:
        print(f"Loaded {len(existing)} stations from existing {ACTIVE_FILENAME.name}")
    else:
        print(f"No existing {ACTIVE_FILENAME.name} found or it's empty.")

    source_path = None
    if args.source:
        source_path = Path(args.source)
        if not source_path.exists():
            print(f"Source file {source_path} not found. Exiting.")
            return
    else:
        if EXPANDED_FALLBACK.exists():
            source_path = EXPANDED_FALLBACK
            print(f"No --source provided; using fallback {EXPANDED_FALLBACK.name}")
        else:
            print("No source CSV provided and no fallback expanded CSV found.")
            print("Please provide a source CSV with the full station list using --source.")
            return

    source_rows = read_csv(source_path)
    if not source_rows:
        print(f"Source file {source_path} contains no rows. Exiting.")
        return
    else:
        print(f"Loaded {len(source_rows)} rows from source {source_path.name}")

    merged_rows, added, updated = merge_stations(existing, source_rows)
    print(f"Merged stations: total {len(merged_rows)} (added {added}, updated {updated})")

    output_path = Path(args.output)
    fieldnames = ["station_id", "station_name", "lines", "interchange"]
    if output_path.exists():
        backup_file(output_path)
    write_csv(output_path, merged_rows, fieldnames)
    print(f"Wrote merged station list to {output_path}")

    if args.activate:
        print("Activating merged file as project's active dmrc_stations_dataset.csv ...")
        backup_file(ACTIVE_FILENAME)
        shutil.copy2(output_path, ACTIVE_FILENAME)
        print(f"Overwrote {ACTIVE_FILENAME} (backup created)")

    print("Done. Please restart your backend to pick up changes if running.")

if __name__ == "__main__":
    main()
