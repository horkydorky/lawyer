import subprocess
import sys
import os
from pathlib import Path

# ============================================================
# CONFIG
# ============================================================

# Project structure
BASE_DIR = Path(__file__).resolve().parent
BACKEND_PATH = BASE_DIR / "backend" / "main.py"
FRONTEND_PATH = BASE_DIR / "frontend"

PYTHON_EXEC = sys.executable  # Use current Python environment

# ============================================================
# RUN BACKEND AND FRONTEND
# ============================================================
# ============================================================
# RUN BACKEND AND FRONTEND
# ============================================================

try:
    print("🚀 Starting backend (FastAPI)...")
    backend_proc = subprocess.Popen(
        [PYTHON_EXEC, "-m", "uvicorn", "backend.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        cwd=BASE_DIR
    )

    # Start frontend:
    # If frontend contains package.json -> assume Node/Vite app and run `npm run dev`
    # Otherwise fall back to Streamlit app at frontend/app.py
    from pathlib import Path as _P
    FRONTEND_DIR = Path(FRONTEND_PATH)
    pkg = FRONTEND_DIR / "package.json"
    if pkg.exists():
        print("🚀 Starting frontend (React/Vite) via `npm run dev`...")
        # Note: requires Node and npm installed in the environment where you run run.py
        Zfrontend_proc = subprocess.Popen("npm run dev", cwd=str(FRONTEND_DIR), shell=True)
    else:
        # Fallback to streamlit app
        print("🚀 Starting frontend (Streamlit)...")
        frontend_proc = subprocess.Popen([PYTHON_EXEC, "-m", "streamlit", "run", str(FRONTEND_DIR / "app.py")], cwd=BASE_DIR)

    print("✅ Both backend and frontend processes started.")
    print("💡 Press Ctrl+C to stop both.")

    # Wait for both processes
    backend_proc.wait()
    frontend_proc.wait()

except KeyboardInterrupt:
    print("\n🛑 Shutting down processes...")
    try:
        backend_proc.terminate()
    except Exception:
        pass
    try:
        frontend_proc.terminate()
    except Exception:
        pass
except Exception as e:
    print(f"⚠️ Error running processes: {e}")
    try:
        backend_proc.terminate()
    except Exception:
        pass
    try:
        frontend_proc.terminate()
    except Exception:
        pass
