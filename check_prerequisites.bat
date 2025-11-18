@echo off
echo ========================================
echo Checking Prerequisites for ACC Telemetry
echo ========================================
echo.

echo Python:
py --version 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo   [X] NOT FOUND
) else (
    echo   [OK] Found
)
echo.

echo pip:
py -m pip --version 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo   [X] NOT FOUND
) else (
    echo   [OK] Found
)
echo.

echo Rust/Cargo:
cargo --version 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo   [X] NOT FOUND - Install from: https://rustup.rs/
) else (
    echo   [OK] Found
)
echo.

echo Visual C++ Compiler (cl.exe):
where cl.exe >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo   [X] NOT FOUND in PATH
    echo   Checking common Visual Studio locations...
    
    if exist "C:\Program Files\Microsoft Visual Studio\2022" (
        echo   [!] Found Visual Studio 2022 installed
    )
    if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019" (
        echo   [!] Found Visual Studio 2019 installed
    )
    if exist "C:\Program Files\Microsoft Visual Studio\2022\BuildTools" (
        echo   [!] Found Build Tools 2022 installed
    )
    
    echo.
    echo   cl.exe not in PATH. You may need to:
    echo   1. Open Visual Studio Installer
    echo   2. Click 'Modify' on your Visual Studio installation
    echo   3. Ensure 'Desktop development with C++' workload is installed
    echo   4. Restart your terminal
) else (
    echo   [OK] Found in PATH
)
echo.

echo ========================================
echo Python Packages Check
echo ========================================
echo.

cd backend 2>nul
if exist requirements.txt (
    echo Checking installed packages from requirements.txt...
    echo.
    
    for /f "tokens=1 delims=><=" %%p in (requirements.txt) do (
        py -m pip show %%p >nul 2>&1
        if !ERRORLEVEL! NEQ 0 (
            echo   [X] %%p - NOT INSTALLED
        ) else (
            echo   [OK] %%p
        )
    )
) else (
    echo requirements.txt not found
)
cd ..

echo.
echo ========================================
echo Summary
echo ========================================
echo.
echo If any items show [X], install them before running setup_windows.bat
echo.
echo Critical requirements:
echo   - Python 3.11+
echo   - Rust/Cargo (for pyaccsharedmemory)
echo   - Visual C++ Build Tools with 'Desktop development with C++' workload
echo.
pause
