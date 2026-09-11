@echo off
echo ============================================================
echo  AIRINDEX — Backend Startup
echo  FastAPI + SQLite (no PostgreSQL needed for dev)
echo ============================================================
echo.

set PYTHON="C:\Users\Chinmay\PyCharmMiscProject\.venv\Scripts\python.exe"

echo [1/2] Installing Python dependencies...
%PYTHON% -m pip install fastapi==0.115.0 "uvicorn[standard]==0.30.6" sqlalchemy==2.0.35 pydantic==2.9.2 python-dotenv==1.0.1 apscheduler==3.10.4

echo.
echo [2/2] Starting FastAPI backend on http://localhost:8000 ...
echo       Docs: http://localhost:8000/docs
echo       Health: http://localhost:8000/api/v1/health
echo.
cd /d "%~dp0"
%PYTHON% -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
