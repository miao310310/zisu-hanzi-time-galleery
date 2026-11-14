@echo off
setlocal
cd /d "%~dp0backend_modelscope"
echo Starting Zisu ModelScope RAG backend: http://127.0.0.1:8000
echo Start the Vue frontend separately with: npm run dev

if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" main.py
) else (
  echo.
  echo Python virtual environment not found.
  echo Follow the backend setup steps in README.md first.
)

pause
endlocal
