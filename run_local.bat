@echo off
cd /d "d:\1.1.1python\16.Physiology SBA - 7 System"
echo Installing requirements...
pip install -r requirements.txt
echo.
echo Starting Physiology SBA app on http://localhost:8000 ...
echo Open in browser: http://localhost:8000
echo Press CTRL+C to stop.
python app.py
pause
