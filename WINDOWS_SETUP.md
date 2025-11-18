# Windows Setup Guide

**IMPORTANT:** ACC telemetry requires Windows shared memory access, so the backend must run **natively on Windows**, not in Docker.

## Prerequisites

1. **Python 3.11+** - Download from https://www.python.org/downloads/
   - During install, check "Add Python to PATH"
2. **Git** - Download from https://git-scm.com/download/win

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/kltalsma/ai-sim-coach-demo.git
   cd ai-sim-coach-demo
   ```

2. **Run setup:**
   ```bash
   setup_windows.bat
   ```

## Running the Dashboard

**Option 1: Automatic (Recommended)**
```bash
run_windows.bat
```
This starts both backend and frontend automatically.

**Option 2: Manual**

Terminal 1 - Backend:
```bash
cd backend
python main.py
```

Terminal 2 - Frontend:
```bash
cd frontend
python -m http.server 8080
```

## Using the Dashboard

1. **Open your browser:** http://localhost:8080
2. **Launch your sim racing game** (ACC, RaceRoom, LMU, or AMS2)
3. **Start any session** (Practice, Qualifying, Race)
4. **Within 5 seconds**, the dashboard will auto-detect and switch to your game!

The game badge (top right) will show which game is active:
- 🔴 Red = ACC
- 🟢 Green = RaceRoom  
- 🔵 Blue = Le Mans Ultimate
- 🟡 Yellow = Automobilista 2
- 🔵 Default Blue = Demo Mode

## Troubleshooting

**"Module not found" errors:**
```bash
cd backend
pip install -r requirements.txt
```

**Dashboard not connecting:**
- Check backend is running on port 5001
- Check frontend is running on port 8080
- Open http://localhost:5001/api/status to verify backend

**Game not detected:**
- Make sure you're in an active session (not just main menu)
- Wait 5-10 seconds for auto-detection
- Check backend console for detection messages

## Stopping

Close both command windows or press Ctrl+C in each terminal.
