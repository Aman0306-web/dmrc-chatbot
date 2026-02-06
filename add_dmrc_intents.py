#!/usr/bin/env python3
"""
add_dmrc_intents.py

Writes dmrc_chatbot_intents_expanded.csv into the current directory.
Options:
  --activate        : also copy/rename the created file to dmrc_chatbot_intents.csv
  --force           : overwrite existing files without prompt
  --git             : run `git add` and `git commit` (and optional push)
  --commit-message  : custom commit message when --git is used (default provided)
  --push            : when used with --git, also run `git push`
Example:
  python add_dmrc_intents.py --activate --git --commit-message "Add expanded intents" --push
"""

import argparse
import os
import subprocess
import sys
from textwrap import dedent

CSV_FILENAME = "dmrc_chatbot_intents_expanded.csv"
ACTIVE_FILENAME = "dmrc_chatbot_intents.csv"

CSV_CONTENT = dedent("""\
intent,example_query
fare_enquiry,What is the fare from Rajiv Chowk to INA?
fare_enquiry,How much does it cost to travel from Kashmere Gate to New Delhi?
fare_enquiry,Metro ticket price from Central Secretariat to Dwarka
last_train,Last metro from Kashmere Gate to Central Secretariat
last_train,What time is the last train from Rajiv Chowk?
last_train,When does the metro close?
route_query,How to go from New Delhi to INA by metro?
route_query,Best route from Kashmere Gate to Rajiv Chowk
route_query,How can I reach airport from Rajiv Chowk?
lost_and_found,I lost my wallet in metro what should I do?
lost_and_found,Where is the lost and found office?
lost_and_found,I left my bag in the metro
helpline,DMRC helpline number
helpline,Customer care contact number
helpline,How to contact metro support?
metro_timings,What time does metro start?
metro_timings,Metro opening and closing timings
metro_timings,First metro from Kashmere Gate
recharge,How to recharge metro card?
recharge,Where can I top up my smart card?
recharge,Online recharge options for metro card
airport,How to reach IGI airport by metro?
airport,Airport Express line route
airport,Metro to Terminal 3
rules,What are the metro rules?
rules,Is eating allowed in metro?
rules,Can I carry a bicycle in metro?
wifi,Is WiFi available in metro stations?
wifi,How to connect to metro WiFi?
wifi,Free internet in metro
parking,Where can I park my car near metro station?
parking,Park and ride facilities
parking,Metro station parking charges
smart_card,What is a smart card?
smart_card,Difference between token and smart card
smart_card,Benefits of metro smart card
peak_hours,What are peak hours in metro?
peak_hours,When is metro most crowded?
peak_hours,Rush hour timings
interchange,Which are interchange stations?
interchange,How to change lines at Rajiv Chowk?
interchange,Transfer between Yellow and Blue line
""")

def write_file(path: str, content: str, force: bool = False):
    if os.path.exists(path) and not force:
        resp = input(f"File '{path}' already exists. Overwrite? [y/N]: ").strip().lower()
        if resp != "y":
            print(f"Skipped writing '{path}'.")
            return False
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print(f"Wrote '{path}' ({os.path.getsize(path)} bytes)")
    return True

def run_git(commands, cwd="."):
    try:
        subprocess.run(["git", "--version"], check=True, stdout=subprocess.DEVNULL)
    except Exception as e:
        print("Git not available or not found in PATH:", e)
        return False

    try:
        for cmd in commands:
            print("Running:", " ".join(cmd))
            subprocess.run(cmd, check=True, cwd=cwd)
        return True
    except subprocess.CalledProcessError as e:
        print("Git command failed:", e)
        return False

def main():
    parser = argparse.ArgumentParser(description="Add dmrc chatbot intents CSV to project")
    parser.add_argument("--activate", action="store_true", help="Also copy to dmrc_chatbot_intents.csv (active filename)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files without prompt")
    parser.add_argument("--git", action="store_true", help="Run git add & commit for the added file(s)")
    parser.add_argument("--commit-message", type=str, default="Add expanded dmrc chatbot intents CSV", help="Commit message when using --git")
    parser.add_argument("--push", action="store_true", help="When used with --git, also run git push")
    args = parser.parse_args()

    wrote = write_file(CSV_FILENAME, CSV_CONTENT, force=args.force)
    activated = False

    if args.activate and wrote:
        # copy/rename
        try:
            with open(CSV_FILENAME, "r", encoding="utf-8") as src, open(ACTIVE_FILENAME, "w", encoding="utf-8", newline="\n") as dst:
                dst.write(src.read())
            print(f"Copied to active filename '{ACTIVE_FILENAME}'")
            activated = True
        except Exception as e:
            print("Failed to copy to active filename:", e)

    if args.git and (wrote or activated):
        files_to_add = [CSV_FILENAME]
        if args.activate:
            files_to_add.append(ACTIVE_FILENAME)
        git_cmds = [["git", "add"] + files_to_add, ["git", "commit", "-m", args.commit_message]]
        if args.push:
            git_cmds.append(["git", "push"])
        success = run_git(git_cmds)
        if not success:
            print("Git operations failed or were not completed.")
    print("Done.")

if __name__ == "__main__":
    main()
