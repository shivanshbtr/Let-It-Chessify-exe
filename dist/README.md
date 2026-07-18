# dist/

This folder is **not stored in this git repo**. It holds the pre-built,
ready-to-run app (`dist/LetItChessify/`) for anyone who'd rather skip
building it themselves and just run the `.exe` directly.

**Download it here:** [drive.google.com/file/d/1xe-0k_YFWtaFtFa55H7sIwoq79OHB64B/view?usp=sharing](https://drive.google.com/file/d/1xe-0k_YFWtaFtFa55H7sIwoq79OHB64B/view?usp=sharing)

## Setup

1. Download the zip from the link above.
2. Extract it so the folder sits here, giving you:

   ```
   Let-It-Chessify-exe/
     dist/
       LetItChessify/
         LetItChessify.exe
         backend/
           models/
             stockfish.exe
         frontend_dist/
           index.html
           assets/
             index-9_hjDrwC.css
             index-D6cssHm_.js
         models/
           corner_detection/train-2/weights/best.pt
           piece_detection/train/weights/best.pt
         runs/
           physical/    label_map.json, square_classifier.onnx(.data)
           synthetic/   label_map.json, square_classifier.onnx(.data)
         _internal/     PyInstaller's bundled Python runtime + libraries
                         (hundreds of DLLs/.pyd files -- not meant to be
                         inspected individually, just kept alongside the exe)
   ```
3. Run `dist\LetItChessify\LetItChessify.exe` — no Python, Node, or build
   step required.

## Why this split

Same reasoning as [`prior_requirements/`](../prior_requirements/README.md):
the built app is large (roughly
1-2GB, mostly OpenCV/Ultralytics/ONNX Runtime plus the trained weights
and Stockfish) and binary-heavy, so it doesn't belong in git. This is
purely a convenience download for people who want the finished app
without running [`build.bat`](../build.bat) themselves — building from
source via the root [`README.md`](../README.md) always produces the
same thing.
