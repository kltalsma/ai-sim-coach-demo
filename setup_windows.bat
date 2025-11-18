@echo off
setlocal enabledelayedexpansion

echo ========================================
echo AI Sim Racing Coach - Windows Setup
echo ========================================
echo.

REM Check if this is first run or package installation run
if "%1"=="--skip-checks" goto PYTHON_PACKAGES

echo Step 1: Checking prerequisites...
echo.

REM Check Python
py --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [X] Python not found!
    echo     Install from: https://www.python.org/downloads/
    pause
    exit /b 1
) else (
    echo [OK] Python found
)

REM Check for Visual C++ Build Tools (check for cl.exe in common locations)
set FOUND_CL=0
where cl.exe >nul 2>&1 && set FOUND_CL=1

if %FOUND_CL%==0 (
    REM Check common VS install locations
    if exist "C:\Program Files\Microsoft Visual Studio" set FOUND_CL=1
    if exist "C:\Program Files (x86)\Microsoft Visual Studio" set FOUND_CL=1
)

if %FOUND_CL%==0 (
    echo [!] Visual C++ Build Tools not detected
    echo     Attempting to install via winget...
    echo.
    winget install Microsoft.VisualStudio.2022.BuildTools --override "--wait --quiet --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"
    echo.
    echo     If installation succeeded, CLOSE this terminal, open a NEW one, and run this script again.
    echo     If installation failed, install manually: https://visualstudio.microsoft.com/visual-cpp-build-tools/
) else (
    echo [OK] Visual C++ Build Tools appear to be installed
    echo     Note: If Python package installation fails, you may need to add the
    echo           'Desktop development with C++' workload via Visual Studio Installer
)

echo.

REM Check Rust/Cargo
cargo --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [!] Rust/Cargo not found
    echo     Attempting to install via winget...
    echo.
    winget install --id Rustlang.Rustup
    echo.
    echo     CLOSE this terminal, open a NEW one, and run this script again.
    pause
    exit /b 0
) else (
    echo [OK] Rust/Cargo found
)

echo.
echo ========================================
echo All prerequisites appear to be installed!
echo Proceeding with Python package installation...
echo ========================================
echo.
timeout /t 2 /nobreak >nul

:PYTHON_PACKAGES

echo Upgrading pip, setuptools, and wheel...
py -m pip install --upgrade pip setuptools wheel
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to upgrade pip
    pause
    exit /b 1
)

echo.
echo Installing backend dependencies...
echo This may take 5-10 minutes on first run (compiling native extensions)
echo.
cd backend
py -m pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================
    echo ERROR: Python package installation failed!
    echo ========================================
    echo.
    echo This usually means Visual C++ Build Tools are missing the required components.
    echo.
    echo Please install the C++ workload manually:
    echo.
    echo 1. Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
    echo 2. Run the installer
    echo 3. Select: 'Desktop development with C++' workload
    echo 4. Click Install
    echo 5. Restart your terminal
    echo 6. Run this script again
    echo.
    echo OR if you already have Visual Studio installed:
    echo 1. Open Visual Studio Installer
    echo 2. Click 'Modify' on your installation
    echo 3. Select 'Desktop development with C++' workload
    echo 4. Click Modify
    echo 5. Restart your terminal
    echo 6. Run this script again
    echo.
    pause
    exit /b 1
)

cd ..

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the dashboard:
echo   run_windows.bat
echo.
echo Or manually:
echo   Terminal 1: cd backend ^&^& py main.py
echo   Terminal 2: cd frontend ^&^& py -m http.server 8080
echo   Then open: http://localhost:8080
echo.
echo Now launch ACC and the dashboard will auto-detect it!
echo.
pause
