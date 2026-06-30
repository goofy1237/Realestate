@echo off
REM ===========================================================================
REM  TEST YOUR DATABASE CONNECTION
REM ===========================================================================
REM  Confirms the tool can reach your shared Supabase database (or that it's
REM  using the local SQLite fallback). Run this after setting up your .env.
REM ===========================================================================
cd /d "%~dp0"
".venv\Scripts\python.exe" -u db_check.py
echo.
pause
