@echo off
REM ===========================================================================
REM  SET UP THE SHARED SUPABASE DATABASE
REM ===========================================================================
REM  Paste your Supabase connection string when asked. It is saved privately
REM  to .env (never committed) and the connection is tested.
REM ===========================================================================
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Please run SETUP.bat first ^(one-time setup^), then try again.
  pause
  exit /b
)
".venv\Scripts\python.exe" -u setup_db.py
echo.
pause
