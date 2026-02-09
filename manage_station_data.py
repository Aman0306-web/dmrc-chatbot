"""
Tool to add new information columns to the DMRC station dataset.
Usage:
    python manage_station_data.py --add-column parking --default "No"
    python manage_station_data.py --set-value "Rajiv Chowk" --column parking --value "Yes, Gate 1"
"""
import csv
import argparse
import shutil
from pathlib import Path
import sys

# Define paths relative to this script
PROJECT_ROOT = Path(__file__).parent.resolve()
CSV_FILE = PROJECT_ROOT / "dmrc_master_stations.csv"
BACKUP_FILE = PROJECT_ROOT / "dmrc_master_stations.csv.bak"

def load_data():
    if not CSV_FILE.exists():
        print(f"Error: {CSV_FILE} not found.")
        return [], []
    
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
    return fieldnames, rows

def save_data(fieldnames, rows):
    # Create backup
    if CSV_FILE.exists():
        shutil.copy2(CSV_FILE, BACKUP_FILE)
    
    with open(CSV_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"✅ Saved changes to {CSV_FILE}")

def add_column(name, default_value):
    fieldnames, rows = load_data()
    if not fieldnames: return

    col_name = name.lower().strip()
    if col_name in fieldnames:
        print(f"⚠️ Column '{col_name}' already exists.")
        return

    fieldnames.append(col_name)
    for row in rows:
        row[col_name] = default_value
    
    save_data(fieldnames, rows)
    print(f"✅ Added column '{col_name}' with default value '{default_value}'")

def set_value(station_name, column, value):
    fieldnames, rows = load_data()
    if not fieldnames: return

    col_name = column.lower().strip()
    if col_name not in fieldnames:
        print(f"❌ Column '{col_name}' does not exist. Use --add-column first.")
        return

    updated = False
    search_name = station_name.lower().strip()
    
    for row in rows:
        curr_name = row.get("station_name", "").lower().strip()
        if curr_name == search_name or search_name in curr_name:
            row[col_name] = value
            updated = True
            print(f"✅ Updated {row['station_name']}: {col_name} = {value}")
            break
    
    if updated:
        save_data(fieldnames, rows)
    else:
        print(f"❌ Station '{station_name}' not found.")

def main():
    parser = argparse.ArgumentParser(description="Manage DMRC Station Data")
    parser.add_argument("--add-column", help="Name of new column to add (e.g., parking)")
    parser.add_argument("--default", help="Default value for new column", default="Unknown")
    parser.add_argument("--set-value", help="Station name to update")
    parser.add_argument("--column", help="Column to update for specific station")
    parser.add_argument("--value", help="Value to set")
    
    args = parser.parse_args()

    if args.add_column:
        add_column(args.add_column, args.default)
    elif args.set_value and args.column and args.value:
        set_value(args.set_value, args.column, args.value)
    else:
        print("Usage Examples:")
        print('  1. Add a new info type: python manage_station_data.py --add-column "parking" --default "No"')
        print('  2. Update a station:    python manage_station_data.py --set-value "Rajiv Chowk" --column "parking" --value "Yes"')

if __name__ == "__main__":
    main()