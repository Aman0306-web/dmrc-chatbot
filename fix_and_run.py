import os
import sys
import subprocess
from pathlib import Path

def main():
    # Ensure we are in the script's directory so relative paths work
    script_dir = Path(__file__).parent.resolve()
    os.chdir(script_dir)

    print("=" * 60)
    print("DMRC 2026 - ONLINE MODE RUN")
    print("=" * 60)

    # 1. Configure for Online Mode
    env_path = Path(".env")
    lines = []
    if env_path.exists():
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:
            print(f"[WARN] Could not read .env: {e}")

    new_lines = []
    found = False
    for line in lines:
        if line.strip().startswith("ASSISTANT_SIMULATE_LIVE="):
            new_lines.append("ASSISTANT_SIMULATE_LIVE=false\n")
            found = True
        else:
            new_lines.append(line)
    
    if not found:
        if new_lines and not new_lines[-1].endswith("\n"):
            new_lines.append("\n")
        new_lines.append("ASSISTANT_SIMULATE_LIVE=false\n")
    
    try:
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print("[CONFIG] Updated .env: ASSISTANT_SIMULATE_LIVE=false")
        print("      (Online Mode Active - Using Real Google CSE API)")
    except Exception as e:
        print(f"[ERROR] Failed to update .env: {e}")
        return

    # Check for data file
    if not Path("dmrc_master_stations.csv").exists():
        print("[WARN] dmrc_master_stations.csv not found! Station data will be limited.")

    # Check if uvicorn is installed
    try:
        import uvicorn
    except ImportError:
        print("[ERROR] 'uvicorn' is not installed. Please run: pip install uvicorn")
        return

    # 2. Run the Application
    print("\n[RUN] Starting Backend Server...")
    print("      Backend:  http://localhost:8000")
    print("      Frontend: http://localhost:3000/index-enhanced.html")
    print("      IMPORTANT: Open a NEW terminal and run: python -m http.server 3000")
    print("      Docs:     http://localhost:8000/docs")
    print("      (Press Ctrl+C to stop)")
    print("-" * 60)
    
    # Force the environment variable for this run
    current_env = os.environ.copy()
    current_env["ASSISTANT_SIMULATE_LIVE"] = "false"

    cmd = [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
    
    try:
        subprocess.run(cmd, env=current_env)
    except KeyboardInterrupt:
        print("\n[STOP] Server stopped.")
    except Exception as e:
        print(f"\n[ERROR] Failed to run server: {e}")
        print("Try installing dependencies: pip install -r requirements.txt")

if __name__ == "__main__":
    main()