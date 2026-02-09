import os
import shutil

def setup():
    print(" organizing DMRC Chatbot Project files...")
    
    # Define required directory structure
    dirs = [
        "templates",
        "static/css",
        "static/js"
    ]
    
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # Map files to their correct locations
    file_moves = {
        "dashboard.html": "templates/dashboard.html",
        "variables.css": "static/css/variables.css",
        "dashboard.css": "static/css/dashboard.css",
        "dashboard.js": "static/js/dashboard.js"
    }

    for src, dst in file_moves.items():
        if os.path.exists(src):
            shutil.move(src, dst)
            print(f"Moved: {src} -> {dst}")
        elif os.path.exists(dst):
            print(f"Verified: {dst} is in place.")
        else:
            print(f"Missing: {src} (Could not find file to move)")

if __name__ == "__main__":
    setup()
    print("\nSetup complete! You can now run 'run_dashboard.bat'.")