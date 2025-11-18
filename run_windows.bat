@echo off
echo ========================================
echo AI Sim Racing Coach - Starting...
echo ========================================
echo.

echo Starting backend server (port 5001)...
start "Backend" cmd /k "cd backend && py main.py"

timeout /t 2 /nobreak >nul

echo Starting frontend server (port 8080)...
start "Frontend" cmd /k "cd frontend && py -m http.server 8080"

timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo Dashboard is starting!
echo ========================================
echo.
echo Backend:  http://localhost:5001
echo Frontend: http://localhost:8080
echo.
echo Two terminal windows have opened.
echo Close them to stop the servers.
echo.
echo Now launch ACC and start a session!
echo The dashboard will auto-detect within 5 seconds.
echo.
pause
