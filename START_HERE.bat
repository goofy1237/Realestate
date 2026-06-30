@echo off
REM ===========================================================================
REM  LUXEBOT PORTAL  —  one window for everything
REM ===========================================================================
REM  Opens the portal. From there: open realestate.com.au to capture, click
REM  "Score now", browse/filter/sort your shortlist, and export to Excel.
REM  Close the portal window to stop.
REM ===========================================================================
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo.
  echo  LuxeBot isn't set up on this computer yet.
  echo  Please run  SETUP.bat  first ^(one-time^), then try again.
  echo.
  pause
  exit /b
)
title LuxeBot Portal
".venv\Scripts\python.exe" -u app.py
pause
