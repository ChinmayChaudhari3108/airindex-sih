@echo off
echo ============================================================
echo  AIRINDEX — Frontend Startup
echo  React + Vite dev server on http://localhost:5173
echo ============================================================
echo.
cd /d "%~dp0"
echo [1/2] Installing Node dependencies (if needed)...
call npm install
echo.
echo [2/2] Starting Vite dev server...
call npm run dev
