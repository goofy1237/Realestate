@echo off
cd /d "%~dp0"
title Liveluxe - Start Here
echo ============================================================
echo    LIVELUXE  -  Acquisition Pipeline
echo ============================================================
echo.
echo Starting the capture receiver in its own window...
start "Liveluxe Receiver (keep this open)" cmd /k ".venv\Scripts\python.exe -u receiver.py"
timeout /t 2 /nobreak >nul

echo Opening realestate.com.au in your browser...
start "" "https://www.realestate.com.au/rent/in-melbourne+cbd,+vic+3000/list-1"
echo.
echo ------------------------------------------------------------
echo  STEP 1 - BROWSE
echo.
echo    Browse the REA rental pages you want (suburbs / filters).
echo    Every page you open is captured automatically - watch the
echo    "Liveluxe Receiver" window to see listings being saved.
echo.
echo    When you have FINISHED browsing, click back on THIS window
echo    and press any key to score everything and open your dashboard.
echo ------------------------------------------------------------
pause >nul

echo.
echo STEP 2 - Adding location scores (about a minute the first time)...
".venv\Scripts\python.exe" -u score_all.py

echo.
echo STEP 3 - Opening your dashboard app...
start "Liveluxe Dashboard (keep this open)" cmd /k ".venv\Scripts\python.exe -u dashboard_app.py"

echo.
echo ============================================================
echo  All done. Keep the Receiver and Dashboard windows open
echo  while you work. Re-run START_HERE any time to capture more.
echo ============================================================
pause
