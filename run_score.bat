@echo off
REM ===========================================================================
REM  ADD LOCATION SCORES  (run after a browsing session)
REM ===========================================================================
REM  Geocodes your captured listings and finalises their scores/verdicts.
REM  Uses the free OpenStreetMap service, so it's gentle and may take a
REM  minute the first time (results are cached for next time).
REM ===========================================================================
cd /d "%~dp0"
".venv\Scripts\python.exe" -u score_all.py
echo.
pause
