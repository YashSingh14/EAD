import subprocess
import sys
import os
import time

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(base_dir, "frontend")
    
    print("========================================")
    print("Starting EchoMind OS")
    print("========================================")
    
    print("[1/2] Starting FastAPI Backend on port 8000...")
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=base_dir
    )
    
    time.sleep(2) # Give backend a moment to initialize
    
    print("[2/2] Starting React Frontend Server...")
    # Using shell=True is important on Windows to resolve npm correctly
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=frontend_dir,
        shell=True
    )
    
    try:
        # Keep the main thread alive while both processes run
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down EchoMind OS...")
        backend_process.terminate()
        frontend_process.terminate()

if __name__ == "__main__":
    main()
