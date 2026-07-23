# Let-It-Chessify-exe

**Original project:** https://github.com/shivanshbtr/Let-It-Chessify

Packages [Let It Chessify](https://github.com/shivanshbtr/Let-It-Chessify)
into a standalone Windows desktop app — one `.exe` that opens in its own
window (via `pywebview`), running the FastAPI backend and the built React
frontend from a single process. No browser, no terminal, no separate
Python/Node setup for end users.

This repo contains only the **packaging additions** on top of the original
project — the launcher script, build automation, and docs. The actual app
source (backend + frontend + trained models + Stockfish) is sourced
unmodified from the original repo and kept separately (see
[`prior_requirements/README.md`](prior_requirements/README.md)) since it's
too large for git.

## Repo layout

```
Let-It-Chessify-exe/
  	desktop_app.py                     Launcher: starts backend + serves frontend + opens window
  	build.bat                                Automates the full Windows build
  	requirements.txt                    pywebview + pyinstaller
  	README.md                       This file
  	prior_requirements/
    		README.md               Points to the Drive-hosted source zip + setup steps
  	dist/
    		README.md               Points to the Drive-hosted pre-built app (optional
            									  -- skip building entirely and just run the .exe)
```

[`prior_requirements/`](prior_requirements/README.md) and
[`dist/`](dist/README.md) are otherwise empty in git -- each folder's
actual contents (source + models + Stockfish, or the pre-built app) live
on Google Drive since both are too large for git. See each folder's
README for the download link and where to extract it.

## Setup

**Don't want to build it yourself?** See
[`dist/README.md`](dist/README.md) for a pre-built, ready-to-run download
instead -- skip straight to running `LetItChessify.exe`.

Otherwise, to build from source:

### 1. Get `prior_requirements/`

Follow [`prior_requirements/README.md`](prior_requirements/README.md) —
download the zip from Google Drive and extract it so
`prior_requirements/` sits right here, next to
[`desktop_app.py`](desktop_app.py).

### 2. Python environment

```bat
python -m venv .venv
.venv\Scripts\activate

pip install -r prior_requirements\backend\requirements.txt
pip install -r requirements.txt
```

Node.js 18+ must also be installed (`node -v` to check) -- the frontend
gets built from source during the build step.

### 3. Build

```bat
.\build.bat
```

This runs, in order: `npm install` → `npm run build` → PyInstaller →
copies model weights, Stockfish, and the built frontend into
`dist\LetItChessify\`, then cleans up intermediate build artifacts
(`build\`, root-level `frontend_dist\`).

Takes a few minutes -- Ultralytics/OpenCV/ONNX Runtime are large, so
PyInstaller's bundling step dominates the time.

### 4. Run it

```
dist\LetItChessify\LetItChessify.exe
```

**Keep the whole `dist\LetItChessify` folder** together, not just the
`.exe` — it depends on the `runs\`, `models\`, `backend\models\`, and
`frontend_dist\` folders sitting next to it.

Total size is roughly 1–2GB. This is expected for a bundled Python +
computer-vision/ML stack: OpenCV, Ultralytics, and ONNX Runtime account
for most of it, with the trained weights and Stockfish making up the
rest.

## What it does at runtime

- Starts the FastAPI backend in-process (no separate server window)
- Serves the pre-built frontend from the same process
- Opens everything in a native window, dark background, with a Windows
  dark title bar where supported
- Keeps a console window visible alongside the app, printing startup
  progress (model loading takes ~10-15s) and any runtime errors
- Runs fully offline -- Stockfish, YOLO weights, and the ONNX classifier
  all load from disk; nothing calls out to the internet
- Live Stockfish analysis streams over a WebSocket as depth increases
  (up to depth 50, capped at 12s per position by default -- toggleable
  in-app, so you can turn the time cap off and let it run to full depth)

## Troubleshooting

**"ModuleNotFoundError" for some package at runtime.**
PyInstaller missed a dynamically-imported module. Add
`--hidden-import <module.name>` to the `pyinstaller` command in
[`build.bat`](build.bat) and rebuild. The error message tells you
exactly which module is missing.

**Stockfish not found / analysis fails / no `[Startup]` log at all.**
Confirm `dist\LetItChessify\backend\models\stockfish.exe` exists after
the build. If Stockfish's startup log never prints at all (not even a
warning), make sure [`desktop_app.py`](desktop_app.py) forwards the
ASGI lifespan event to the mounted backend app
(`FastAPI(lifespan=lifespan)` wrapping `api_app.router.lifespan_context`)
-- without it, the backend's `@app.on_event("startup")` handler that
loads Stockfish silently never runs.

**Blank window / app doesn't load.**
Check `dist\LetItChessify\frontend_dist\index.html` exists. If missing,
`npm run build` failed or wasn't copied -- re-run [`build.bat`](build.bat)
and watch steps 1-3 for errors.

**Antivirus / SmartScreen flags the .exe.**
Expected for unsigned PyInstaller executables, especially large ones.
Users will need to click "More info -> Run anyway" the first time.

**Analysis feels slow / freezes when moving pieces quickly.**
Each analysis is capped at depth 50 or 12 seconds by default (see
`StockfishEngine(depth=50, move_time=12)` in
[`prior_requirements/backend/main.py`](prior_requirements/backend/main.py)).
Moving to a new position cancels the previous still-running analysis
rather than letting it finish unattended. The 12s cap can also be turned
off directly in the app (a toggle on the Analysis screen: "Max analysis
limit per position: 12s") to let a position run to full depth instead --
useful for a single position you want a stronger read on, though of
course each analysis then takes longer.

## License

MIT

