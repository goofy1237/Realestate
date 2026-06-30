@echo off
REM ===========================================================================
REM  LUXEBOT PORTAL  —  one window for everything
REM ===========================================================================
REM  Opens the portal. From there: open realestate.com.au to capture, click
REM  "Score now", browse/filter/sort your shortlist, and export to Excel.
REM  Close the portal window to stop.
REM ===========================================================================
cd /d "%~dp0"
title LuxeBot Portal
".venv\Scripts\python.exe" -u app.py
pause
