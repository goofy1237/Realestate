@echo off
REM ===========================================================================
REM  TEST YOUR DATABASE CONNECTION
REM ===========================================================================
REM  Confirms the tool can reach your shared Supabase database (or that it's
REM  using the local SQLite fallback). Run this after setting up your .env.
REM ===========================================================================
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Please run SETUP.bat first ^(one-time setup^), then try again.
  pause
  exit /b
)
".venv\Scripts\python.exe" -u db_check.py
echo.
pause
