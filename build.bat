@echo off
setlocal

REM ============================================================
REM  Let It Chessify - Windows .exe build script
REM  Run this from the project root (same folder as desktop_app.py).
REM  Expects:
REM    prior_requirements\backend\
REM    prior_requirements\frontend\
REM    prior_requirements\models\
REM    prior_requirements\runs\
REM  Assumes: venv already created + activated, and
REM           prior_requirements\backend\models\stockfish.exe already placed.
REM ============================================================

set SRC=prior_requirements

echo.
echo === [1/5] Installing frontend dependencies (npm install) ===
pushd %SRC%\frontend
call npm install
if errorlevel 1 goto :error
popd

echo.
echo === [2/5] Building frontend (npm run build) ===
pushd %SRC%\frontend
call npm run build
if errorlevel 1 goto :error
popd

echo.
echo === [3/5] Copying frontend build output ===
if exist frontend_dist rmdir /s /q frontend_dist
xcopy /E /I /Y %SRC%\frontend\dist frontend_dist
if errorlevel 1 goto :error

if not exist %SRC%\backend\models\stockfish.exe (
    echo.
    echo *** ERROR: %SRC%\backend\models\stockfish.exe not found. ***
    echo Place your Stockfish Windows binary there before building.
    goto :error
)

echo.
echo === [4/5] Running PyInstaller ===
if exist build rmdir /s /q build
if exist dist\LetItChessify rmdir /s /q dist\LetItChessify

pyinstaller desktop_app.py ^
  --name LetItChessify ^
  --onedir ^
  --noconfirm ^
  --paths %SRC% ^
  --collect-all ultralytics ^
  --collect-all onnxruntime ^
  --collect-all cv2 ^
  --collect-all chess ^
  --hidden-import uvicorn.logging ^
  --hidden-import uvicorn.loops ^
  --hidden-import uvicorn.loops.auto ^
  --hidden-import uvicorn.protocols ^
  --hidden-import uvicorn.protocols.http ^
  --hidden-import uvicorn.protocols.http.auto ^
  --hidden-import uvicorn.protocols.websockets ^
  --hidden-import uvicorn.protocols.websockets.auto ^
  --hidden-import uvicorn.lifespan ^
  --hidden-import uvicorn.lifespan.on
if errorlevel 1 goto :error

echo.
echo === [5/5] Copying model weights, Stockfish, and frontend into dist\LetItChessify ===
xcopy /E /I /Y %SRC%\runs dist\LetItChessify\runs
xcopy /E /I /Y %SRC%\models dist\LetItChessify\models
xcopy /E /I /Y frontend_dist dist\LetItChessify\frontend_dist
mkdir dist\LetItChessify\backend\models
copy /Y %SRC%\backend\models\stockfish.exe dist\LetItChessify\backend\models\stockfish.exe

echo.
echo === Cleaning up intermediate build artifacts ===
if exist build rmdir /s /q build
if exist frontend_dist rmdir /s /q frontend_dist

echo.
echo ============================================================
echo  BUILD COMPLETE
echo  Your app is at: dist\LetItChessify\LetItChessify.exe
echo  Distribute the WHOLE "dist\LetItChessify" folder, not just
echo  the .exe -- the models/runs/frontend_dist/backend folders
echo  next to it are required at runtime.
echo ============================================================
goto :eof

:error
echo.
echo *** BUILD FAILED - see the error above. ***
exit /b 1
