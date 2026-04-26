@echo off
REM Start SnapLearn FastAPI on port 8000 (Vite proxy expects this).
cd /d "%~dp0"
if not exist ".env" (
  echo No backend\.env found. Create backend\.env with GOOGLE_API_KEY or GEMINI_API_KEY and GEMINI_MODEL.
  pause
  exit /b 1
)
echo Starting API at http://127.0.0.1:8000 ...
python main.py
pause
