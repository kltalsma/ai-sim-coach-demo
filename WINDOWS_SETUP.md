# Windows Setup Guide

**IMPORTANT:** ACC telemetry requires Windows shared memory access, so the backend must run **natively on Windows**, not in Docker.

## Prerequisites

### Required

1. **Python 3.11+** - Download from https://www.python.org/downloads/
   - During install, check "Add Python to PATH"
   
2. **Microsoft Visual C++ Build Tools** - Required for ACC telemetry
   - Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Install the **"Desktop development with C++"** workload
   - This is needed to compile pydantic-core and pyaccsharedmemory

3. **Rust and Cargo** - Required for pyaccsharedmemory
   - Download: https://rustup.rs/
   - Follow the installation instructions
   - Restart your terminal after installation

### Optional

4. **Git** - Download from https://git-scm.com/download/win
   - Only needed if cloning from GitHub

## Installation Steps

1. **Install Prerequisites (if not already installed):**
   - Python 3.11+ (check "Add Python to PATH")
   - Visual C++ Build Tools ("Desktop development with C++" workload)
   - Rust/Cargo from rustup.rs
   - **Restart your terminal** after installing these tools

2. **Clone or download the repository:**
   /Users/kltalsma/ai-sim-coach-demo

3. **Run setup:**
   
   
   The script will:
   - Upgrade pip, setuptools, and wheel
   - Install all Python dependencies including pyaccsharedmemory
   - Show clear error messages if anything is missing

## Running the Dashboard

**Option 1: Automatic (Recommended)**

This starts both backend and frontend automatically.

**Option 2: Manual**

Terminal 1 - Backend:


Terminal 2 - Frontend:


## Using the Dashboard

1. **Open your browser:** http://localhost:8080
2. **Launch ACC** (Assetto Corsa Competizione)
3. **Start any session** (Practice, Qualifying, Race)
4. **Within 5 seconds**, the dashboard will auto-detect ACC and display live telemetry!

The game badge (top right) will show which game is active:
- 🔴 Red = ACC
- 🟢 Green = RaceRoom  
- 🔵 Blue = Le Mans Ultimate
- 🟡 Yellow = Automobilista 2
- 🔵 Default Blue = Demo Mode

## Troubleshooting

### "Failed to build wheel for pydantic-core" or "pyaccsharedmemory"

**Solution:** Install Microsoft Visual C++ Build Tools
1. Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Run installer and select **"Desktop development with C++"**
3. Restart terminal after installation
4. Run  again

### "cargo not found" or Rust errors

**Solution:** Install Rust/Cargo
1. Download: https://rustup.rs/
2. Follow installation instructions
3. **Restart terminal** after installation
4. Run  again

### "Module not found" errors



### Dashboard not connecting

- Check backend is running on port 5001
- Check frontend is running on port 8080
- Open http://localhost:5001/api/status to verify backend

### Game not detected

- Make sure you're in an active session (not just main menu)
- Wait 5-10 seconds for auto-detection
- Check backend console for detection messages
- Verify ACC is configured to share telemetry data

## Stopping

Close both command windows or press Ctrl+C in each terminal.

## Notes

- The setup process requires compilation of native Python extensions
- This is why Docker won't work - ACC shared memory is Windows-only
- First-time setup may take 5-10 minutes to compile all dependencies
- Subsequent runs will be fast since packages are already compiled
