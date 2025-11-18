@echo off
echo ========================================
echo AI Sim Racing Coach - Starting...
echo ========================================
echo.

echo Starting backend...
cd backend
start "Backend" python main.py

timeout /t 3

echo Starting frontend...
cd ../frontend
start "Frontend" python -m http.server 8080

echo.
echo ========================================
echo Dashboard: http://localhost:8080
echo Backend API: http://localhost:5001
echo.
echo Close these windows to stop the servers
echo ========================================
pause
