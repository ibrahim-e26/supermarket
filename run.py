import subprocess
import sys
import time

def main():
    print("🚀 Starting Supermarket System...")

    # Start FastAPI Backend
    print("📦 Starting FastAPI Backend...")
    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--reload", "--port", "8000"]
    )
    
    # Wait a moment for the backend to initialize
    time.sleep(2)
    
    # Start Streamlit Frontend
    print("🎨 Starting Streamlit Frontend...")
    frontend = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "frontend/app.py"]
    )
    
    print("\n✅ Both services are running!")
    print("Backend API: http://localhost:8000")
    print("Frontend UI: http://localhost:8501")
    print("Press Ctrl+C to stop both services.\n")
    
    try:
        # Keep the script running to maintain the subprocesses
        backend.wait()
        frontend.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        backend.terminate()
        frontend.terminate()
        backend.wait()
        frontend.wait()
        print("Services stopped.")
        sys.exit(0)

if __name__ == "__main__":
    main()
