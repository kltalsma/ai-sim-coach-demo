@echo off
echo ========================================
echo AI Sim Racing Coach - Windows Setup
echo ========================================
echo.

echo Installing Python dependencies...
cd backend
pip install -r requirements.txt

echo.
echo ========================================
echo Setup complete!
echo.
echo To start the backend:
echo   cd backend
echo   python main.py
echo.
echo Then open: http://localhost:8080
echo ========================================
pause
