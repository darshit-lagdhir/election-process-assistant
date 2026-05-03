import os
import subprocess
import time
import sys

def ignite():
    """The Master Ignition Sequence: Unified entry point for the Hadron Core."""
    print("!!! HADRON CORE: SOVEREIGN IGNITION INITIATED !!!")
    
    # 1. Neutralize Socket Collisions (Only on Local/Windows)
    if sys.platform == "win32":
        print("[1/3] Neutralizing Socket Collisions (Port 8000)...")
        subprocess.run(["powershell", "-Command", 
                        "Stop-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess -Force -ErrorAction SilentlyContinue"],
                       capture_output=True)
    else:
        print("[1/3] Linux/Production Environment Detected. Skipping Socket Neutralization.")
    
    # 2. Verify Environment
    print("[2/3] Verifying Environment Context...")
    if not os.path.exists(".env") and not os.getenv("GOOGLE_API_KEY"):
        print("!!! WARNING: Environment configuration missing. Creating fallback...")
        with open(".env", "w") as f:
            f.write("GOOGLE_API_KEY=YOUR_KEY_HERE\n")
            
    # 3. Ignite Kernel Citadel
    print("[3/3] Igniting Kernel Citadel via Uvicorn...")
    port = os.getenv("PORT", "8000")
    try:
        # Launching the modular API Gateway
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "backend.api.app:app", 
            "--host", "0.0.0.0", 
            "--port", str(port)
        ])
    except KeyboardInterrupt:
        print("\n!!! HADRON CORE: SYSTEMIC EXTINCTION COMPLETE !!!")
    except Exception as e:
        print(f"\n!!! KERNEL PANIC: {e} !!!")

if __name__ == "__main__":
    ignite()
