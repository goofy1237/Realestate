@echo off
REM ===========================================================================
REM  OPEN THE DASHBOARD
REM ===========================================================================
REM  Double-click this. It opens your ranked shortlist in your browser and
REM  keeps a small window running in the background. Close the window (or
REM  press Ctrl+C) to stop the dashboard.
REM ===========================================================================
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Please run SETUP.bat first ^(one-time setup^), then try again.
  pause
  exit /b
)
".venv\Scripts\python.exe" -u dashboard_app.py
pause
