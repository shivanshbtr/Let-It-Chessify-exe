# prior_requirements/

This folder is **not stored in this git repo** — it contains the trained
model weights, Stockfish binary, and app source, which together push the
folder size well past what's reasonable to keep in git (mostly due to
`stockfish.exe`, ~110MB).

All files here are sourced directly, unmodified in content, from the
original project repo — **https://github.com/shivanshbtr/Let-It-Chessify**
— zipped and hosted on Google Drive since GitHub isn't a good fit for a
folder this size.

**Download it here:** [https://drive.google.com/file/d/1Wz3nW6SCnbdArhjH8ozAiHE8LqAlpjtW/view?usp=sharing](https://drive.google.com/file/d/1Wz3nW6SCnbdArhjH8ozAiHE8LqAlpjtW/view?usp=sharing)

## Setup

1. Download the zip from the link above.
2. Extract it so `prior_requirements/` sits at the root of
   `Let-It-Chessify-exe/`, next to [`desktop_app.py`](../desktop_app.py) and
   [`build.bat`](../build.bat) — i.e.
   the final layout should be:

   ```
   Let-It-Chessify-exe/
     	desktop_app.py
     	build.bat
     	requirements.txt
     	README.md
     	prior_requirements/        <- extracted here
       	backend/
       	frontend/
       	models/
       	runs/
   ```
3. Continue with the setup steps in the root [`README.md`](../README.md).

## What's inside

```
prior_requirements/
├── backend/
│   │   engine.py            Stockfish wrapper (analysis, live streaming)
│   │   main.py               FastAPI app -- all API + WebSocket endpoints
│   │   requirements.txt
│   │   __init__.py
│   │
│   ├───detection/            Corner detection, piece detection, classification
│   │       board_mapper.py
│   │       chessboard_grid_segmentation.py
│   │       classical_cv.py
│   │       classifier.py
│   │       corner_detector.py
│   │       fen.py
│   │       piece_detector.py
│   │       preprocessing.py
│   │       __init__.py
│   │
│   └───models/
│           stockfish.exe     Stockfish Windows binary (~110MB)
│
├── frontend/
│   │   index.html
│   │   package-lock.json
│   │   package.json
│   │   vite.config.js
│   │
│   └───src/
│       │   App.jsx
│       │   index.css
│       │   main.jsx
│       │
│       ├───api/
│       │       chess.js
│       │
│       ├───components/
│       │       AnalysisStep.jsx
│       │       BoardEditorStep.jsx
│       │       CornerConfirmStep.jsx
│       │       ScoreBar.jsx
│       │       StepIndicator.jsx
│       │       TurnSelectStep.jsx
│       │       UploadStep.jsx
│       │
│       └───hooks/
│               useSquareFit.js
│
├── models/                   Trained YOLO weights (corner + piece detection)
│   ├───corner_detection/train-2/weights/
│   │       best.pt
│   └───piece_detection/train/weights/
│           best.pt
│
└── runs/                     Trained ONNX square classifiers
    ├───physical/
    │       label_map.json
    │       square_classifier.onnx
    │       square_classifier.onnx.data
    └───synthetic/
            label_map.json
            square_classifier.onnx
            square_classifier.onnx.data
```

Note: no `frontend/dist/` here — [`build.bat`](../build.bat) builds the
frontend fresh from source (`npm install` + `npm run build`) every time,
so a pre-built copy isn't needed in this zip.

## Why this split

- [`desktop_app.py`](../desktop_app.py), [`build.bat`](../build.bat), and
  the root [`README.md`](../README.md) stay in git — small, text-only,
  worth version-controlling normally.
- `prior_requirements/` (models + Stockfish binary + app source, sourced
  from the original repo) stays on Drive — binary-heavy, doesn't diff
  meaningfully in git, and Stockfish alone exceeds GitHub's comfortable
  file-size range.
