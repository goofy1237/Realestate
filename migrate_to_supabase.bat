@echo off
REM ===========================================================================
REM  MIGRATE LOCAL LISTINGS INTO SUPABASE
REM ===========================================================================
REM  Copies everything from your local listings.db into the shared Supabase
REM  database (set up .env first). Safe to run more than once.
REM ===========================================================================
cd /d "%~dp0"
".venv\Scripts\python.exe" -u migrate_to_supabase.py
echo.
pause
