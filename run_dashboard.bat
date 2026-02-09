@echo off
TITLE MetroSahayak Dashboard

echo =================================================
echo    STARTING DMRC METRO ASSISTANT (FLASK)
echo =================================================
echo.
echo 1. Checking dependencies...
pip install -r requirements.txt
echo.
echo 2. Launching Server...
python app.py
pause