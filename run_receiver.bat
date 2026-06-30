@echo off
REM ===========================================================================
REM  RUN THE LOCAL RECEIVER
REM ===========================================================================
REM  Double-click this, then leave the black window open while you browse
REM  realestate.com.au. It catches the listing data the extension sends.
REM  Press Ctrl+C in the window (or just close it) to stop.
REM ===========================================================================
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Please run SETUP.bat first ^(one-time setup^), then try again.
  pause
  exit /b
)
".venv\Scripts\python.exe" -u receiver.py
pause
