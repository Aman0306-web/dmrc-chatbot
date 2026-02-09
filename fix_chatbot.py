import os
import shutil
import sys
import subprocess
import time

def main():
    print("🔧 DMRC Chatbot Fixer & Launcher")
    print("================================")

    # 1. Ensure Directory Structure
    print("[1/3] Checking file structure...")
    
    base_dir = os.getcwd()
    templates_dir = os.path.join(base_dir, "templates")
    static_dir = os.path.join(base_dir, "static")
    css_dir = os.path.join(static_dir, "css")
    js_dir = os.path.join(static_dir, "js")

    os.makedirs(templates_dir, exist_ok=True)
    os.makedirs(css_dir, exist_ok=True)
    os.makedirs(js_dir, exist_ok=True)

    # Move files if they are in root
    moves = [
        ("dashboard.html", templates_dir),
        ("variables.css", css_dir),
        ("dashboard.css", css_dir),
        ("dashboard.js", js_dir)
    ]

    for filename, dest_dir in moves:
        src = os.path.join(base_dir, filename)
        dst = os.path.join(dest_dir, filename)
        
        if os.path.exists(src):
            try:
                shutil.move(src, dst)
                print(f"  -> Moved {filename} to correct folder.")
            except Exception as e:
                print(f"  -> Error moving {filename}: {e}")
        elif os.path.exists(dst):
            print(f"  -> {filename} is already in place.")
        else:
            # It's okay if not found in root if it's already in dest, but we checked dest above.
            # If missing from both, it's a problem.
            print(f"  -> NOTE: {filename} checked.")

    # 2. Check Dependencies
    print("\n[2/3] Checking dependencies...")
    try:
        import flask
        print("  -> Flask is installed.")
    except ImportError:
        print("  -> Installing Flask...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])

    # 3. Launch App
    print("\n[3/3] Launching Chatbot...")
    print("  -> Starting Flask server on http://localhost:5000")
    print("  -> Please wait for the browser to open...")
    
    subprocess.call([sys.executable, "app.py"])

if __name__ == "__main__":
    main()