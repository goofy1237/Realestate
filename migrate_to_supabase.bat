@echo off
REM ===========================================================================
REM  MIGRATE LOCAL LISTINGS INTO SUPABASE
REM ===========================================================================
REM  Copies everything from your local listings.db into the shared Supabase
REM  database (set up .env first). Safe to run more than once.
REM ===========================================================================
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Please run SETUP.bat first ^(one-time setup^), then try again.
  pause
  exit /b
)
".venv\Scripts\python.exe" -u migrate_to_supabase.py
echo.
pause
