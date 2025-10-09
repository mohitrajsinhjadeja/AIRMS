import subprocess
import sys
import os
from pathlib import Path

def start_server():
    try:
        # Get the backend directory
        backend_dir = Path(__file__).parent.parent
        
        # Activate virtual environment if needed
        if "VIRTUAL_ENV" not in os.environ:
            print("⚠️ Virtual environment not activated!")
            venv_path = backend_dir / "venv" / "Scripts" / "activate"
            if venv_path.exists():
                print(f"Please run: {venv_path}")
            return False
        
        # Start the FastAPI server
        print("🚀 Starting AIRMS+ Backend server...")
        subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--reload"],
            cwd=backend_dir
        )
        
        print("✅ Server started! Running on http://localhost:8000")
        return True
        
    except Exception as e:
        print(f"❌ Error starting server: {str(e)}")
        return False

if __name__ == "__main__":
    start_server()