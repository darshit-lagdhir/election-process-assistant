import os
import subprocess
import time
import sys

def ignite():
    """The Master Ignition Sequence: Unified entry point for the Hadron Core."""
    print("!!! HADRON CORE: SOVEREIGN IGNITION INITIATED !!!")
    
    # 1. Neutralize Socket Collisions
    print("[1/3] Neutralizing Socket Collisions (Port 8000)...")
    if sys.platform == "win32":
        subprocess.run(["powershell", "-Command", 
                        "Stop-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess -Force -ErrorAction SilentlyContinue"],
                       capture_output=True)
    
    # 2. Verify Environment
    print("[2/3] Verifying Environment (.env)...")
    if not os.path.exists(".env"):
        print("!!! WARNING: .env missing. Creating fallback...")
        with open(".env", "w") as f:
            f.write("GOOGLE_API_KEY=YOUR_KEY_HERE\n")
            
    # 3. Ignite Kernel
    print("[3/3] Igniting Kernel Citadel...")
    try:
        subprocess.run([sys.executable, "-m", "backend.main"])
    except KeyboardInterrupt:
        print("\n!!! HADRON CORE: SYSTEMIC EXTINCTION COMPLETE !!!")

if __name__ == "__main__":
    ignite()
