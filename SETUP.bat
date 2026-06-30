@echo off
REM ===========================================================================
REM  LUXEBOT - FIRST-TIME SETUP  (run this ONCE on each computer)
REM ===========================================================================
cd /d "%~dp0"
echo ============================================================
echo    LuxeBot - First-time setup
echo ============================================================
echo.
echo Checking for Python...
python --version
if errorlevel 1 (
  echo.
  echo  ^>^>^> Python is NOT installed ^(or not on PATH^).
  echo  1^) Install it from https://www.python.org/downloads/
  echo  2^) During install, TICK "Add python.exe to PATH"
  echo  3^) Then run SETUP again.
  echo.
  pause
  exit /b
)

echo.
echo Creating the environment and installing the tool's parts...
echo  ^>^>^> THIS CAN TAKE 2-10 MINUTES. Please WAIT. Do NOT close this window. ^<^<^<
echo  ^>^>^> It may look frozen for a while - that's normal. ^<^<^<
echo.

python -m venv .venv
if errorlevel 1 (
  echo  Could not create the environment. Make sure Python installed correctly.
  pause
  exit /b
)

".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo  Something went wrong installing the parts. Check your internet and
  echo  run SETUP again.
  pause
  exit /b
)

echo.
echo ============================================================
echo   SETUP COMPLETE!
echo.
echo   Next steps:
echo     1^) run  setup_db.bat   ^(paste your Supabase connection string^)
echo     2^) run  START_HERE.bat ^(opens the portal^)
echo ============================================================
pause
