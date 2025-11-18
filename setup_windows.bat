@echo off
setlocal enabledelayedexpansion

echo ========================================
echo AI Sim Racing Coach - Windows Setup
echo ========================================
echo.

REM Check if this is first run or package installation run
if "%1"=="--packages-only" goto PYTHON_PACKAGES

echo Step 1: Checking prerequisites...
echo.

REM Check Python
py --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [X] Python not found!
    echo     Install from: https://www.python.org/downloads/
    set MISSING=1
) else (
    echo [OK] Python found
)

REM Check Visual C++ Build Tools (check for cl.exe)
where cl.exe >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [X] Visual C++ Build Tools not found
    set NEED_BUILDTOOLS=1
    set MISSING=1
) else (
    echo [OK] Visual C++ Build Tools found
)

REM Check Rust/Cargo
cargo --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [X] Rust/Cargo not found
    set NEED_RUST=1
    set MISSING=1
) else (
    echo [OK] Rust/Cargo found
)

echo.

if defined MISSING (
    echo ========================================
    echo Missing Prerequisites
    echo ========================================
    echo.
    
    if defined NEED_BUILDTOOLS (
        echo Installing Visual C++ Build Tools via winget...
        winget install Microsoft.VisualStudio.2022.BuildTools --override "--wait --quiet --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"
        
        if !ERRORLEVEL! NEQ 0 (
            echo.
            echo Failed to install automatically. Please install manually:
            echo https://visualstudio.microsoft.com/visual-cpp-build-tools/
            echo Select: 'Desktop development with C++' workload
            echo.
        )
    )
    
    if defined NEED_RUST (
        echo Installing Rust via winget...
        winget install --id Rustlang.Rustup
        
        if !ERRORLEVEL! NEQ 0 (
            echo.
            echo Failed to install automatically. Please install manually:
            echo https://rustup.rs/
            echo.
        )
    )
    
    echo.
    echo ========================================
    echo IMPORTANT: Restart Required
    echo ========================================
    echo.
    echo Please CLOSE this terminal and open a NEW one.
    echo Then run this script again to install Python packages.
    echo.
    pause
    exit /b 0
)

:PYTHON_PACKAGES
echo Step 2: Installing Python packages...
echo.

echo Upgrading pip, setuptools, and wheel...
py -m pip install --upgrade pip setuptools wheel
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to upgrade pip
    pause
    exit /b 1
)

echo.
echo Installing backend dependencies (this may take a few minutes)...
cd backend
py -m pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================
    echo ERROR: Installation failed!
    echo ========================================
    echo.
    echo Possible solutions:
    echo 1. Make sure you RESTARTED your terminal after installing build tools
    echo 2. Check that Visual C++ Build Tools includes 'Desktop development with C++'
    echo 3. Verify Rust is installed: cargo --version
    echo.
    echo If problems persist, install manually:
    echo   Visual C++ Build Tools: https://visualstudio.microsoft.com/visual-cpp-build-tools/
    echo   Rust: https://rustup.rs/
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
pause
