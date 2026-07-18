"""
Let It Chessify — Desktop App Launcher
=======================================
Runs the FastAPI backend and serves the built React frontend from a single
process, then opens everything in a native app window (via pywebview) —
no separate terminal, no browser tab.

Dev (run straight from source):
    python desktop_app.py

Frozen (after PyInstaller build):
    LetItChessify.exe

See BUILD_WINDOWS.md for how to package this into a .exe.
"""
import sys
import os

os.environ["PYTHONUNBUFFERED"] = "1"
try:
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
except Exception:
    pass

import time
import threading
from pathlib import Path


def get_base_dir() -> Path:
    """Folder the exe (or this script) lives in — every data path is
    resolved relative to this, NOT to backend/main.py's __file__, because
    __file__ resolution breaks once the code is frozen by PyInstaller."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent.resolve()


BASE_DIR = get_base_dir()

# Point every model / label-map / engine path at files shipped next to the
# exe. backend/main.py and backend/engine.py already support these env vars.
os.environ.setdefault("SYNTHETIC_MODEL_PATH", str(BASE_DIR / "runs" / "synthetic" / "square_classifier.onnx"))
os.environ.setdefault("SYNTHETIC_LABEL_MAP_PATH", str(BASE_DIR / "runs" / "synthetic" / "label_map.json"))
os.environ.setdefault("PHYSICAL_MODEL_PATH", str(BASE_DIR / "runs" / "physical" / "square_classifier.onnx"))
os.environ.setdefault("PHYSICAL_LABEL_MAP_PATH", str(BASE_DIR / "runs" / "physical" / "label_map.json"))
os.environ.setdefault("CORNER_MODEL_PATH", str(BASE_DIR / "models" / "corner_detection" / "train-2" / "weights" / "best.pt"))
os.environ.setdefault("PIECE_DETECTION_MODEL_PATH", str(BASE_DIR / "models" / "piece_detection" / "train" / "weights" / "best.pt"))
os.environ.setdefault("STOCKFISH_PATH", str(BASE_DIR / "backend" / "models" / "stockfish.exe"))

# Make sure the `backend` package is importable.
# Source layout: <project_root>/prior_requirements/backend/...
# Frozen layout: PyInstaller bundles the `backend` package internally
# regardless of where it lived in source, so no path fixup is needed there.
if not getattr(sys, "frozen", False):
    SRC_DIR = BASE_DIR / "prior_requirements"
    if str(SRC_DIR) not in sys.path:
        sys.path.insert(0, str(SRC_DIR))

import uvicorn  # noqa: E402
from contextlib import asynccontextmanager  # noqa: E402
from fastapi import FastAPI  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402

from backend.main import app as api_app  # noqa: E402  (import after env setup above)

# Where the built frontend (`npm run build` output) lives. build.bat copies
# frontend/dist here automatically.
FRONTEND_DIST = BASE_DIR / "frontend_dist"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # IMPORTANT: mounting api_app as a sub-application (app.mount below)
    # does NOT forward the ASGI "lifespan" event to it by default -- only
    # HTTP/WebSocket traffic gets forwarded. Without this, api_app's
    # @app.on_event("startup") handler (which loads Stockfish, prints the
    # [Startup] lines, etc.) would silently never run at all.
    async with api_app.router.lifespan_context(api_app):
        yield


app = FastAPI(lifespan=lifespan)
# Backend keeps its original routes (e.g. /health, /detect-corners) — mount
# it under /api so it matches what the frontend already calls (BASE = '/api').
app.mount("/api", api_app)
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="static")
else:
    print(f"[desktop_app] WARNING: {FRONTEND_DIST} not found. "
          f"Run 'npm run build' in frontend/ and copy dist/ here as 'frontend_dist'.")

PORT = 8000


def run_server():
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")


def wait_for_server(url: str, timeout: float = 30.0) -> bool:
    import urllib.request
    start = time.time()
    while time.time() - start < timeout:
        try:
            urllib.request.urlopen(url, timeout=1)
            return True
        except Exception:
            time.sleep(0.3)
    return False


def main():
    print("[desktop_app] Starting Let It Chessify... loading models, this takes ~10-15s.")

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    if not wait_for_server(f"http://127.0.0.1:{PORT}/api/health"):
        print("[desktop_app] WARNING: backend didn't respond in time, opening window anyway.")

    import webview  # imported late so `python desktop_app.py --help`-type debugging doesn't need it
    window = webview.create_window(
        "Let It Chessify",
        f"http://127.0.0.1:{PORT}/",
        width=1280,
        height=860,
        min_size=(900, 600),
        background_color="#1a1a1a",  # dark loading background instead of a white flash
    )

    if sys.platform == "win32":
        _try_enable_dark_titlebar(window)

    webview.start()

    # Window closed -> hard-exit the whole process (kills the daemon
    # server thread with it). Plain sys.exit() would hang on the thread.
    os._exit(0)


def _try_enable_dark_titlebar(window):
    """Best-effort: ask Windows to draw the native title bar/border in dark
    mode (Windows 10 20H1+ / 11 only). Safe no-op everywhere else -- if the
    pywebview version or Windows build doesn't support this, we just keep
    the default title bar instead of crashing the app over cosmetics."""
    def apply():
        try:
            import ctypes
            hwnd = window.native.Handle.ToInt32() if hasattr(window.native, "Handle") else int(window.native)
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            value = ctypes.c_int(1)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(value), ctypes.sizeof(value)
            )
        except Exception:
            pass  # cosmetic only -- never let this break app startup

    window.events.shown += apply


if __name__ == "__main__":
    main()
