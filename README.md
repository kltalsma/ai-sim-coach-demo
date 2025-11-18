# AI Sim Racing Coach Dashboard

Real-time telemetry dashboard and AI coaching system for sim racing.

## Supported Games
- ✅ **ACC** (Assetto Corsa Competizione) - Shared Memory
- ✅ **RaceRoom** (R3E) - Shared Memory
- ✅ **Le Mans Ultimate** (LMU) - rFactor 2 Shared Memory
- ✅ **Automobilista 2** (AMS2) - UDP Telemetry

## Features

### Dashboard
- 📊 Real-time telemetry display (Speed, RPM, Gear, Inputs)
- 🏁 Track status with flag indicators
- 🎯 Live leaderboard with position and gap information
- 🔥 Tire and brake temperature monitoring with color coding
- ⛽ Fuel management and lap estimation
- 📍 Live track map with car position
- ⏱️ Lap times and sector deltas
- 🎮 THR/BRK/Clutch input visualization

### AI Coaching (Planned)
- Real-time coaching messages based on telemetry
- Tire management advice
- Fuel strategy recommendations
- Brake point optimization
- Technique analysis

## Architecture

```
┌─────────────────┐
│   Racing Sim    │
│  (ACC/R3E/LMU/  │
│     AMS2)       │
└────────┬────────┘
         │ Shared Memory / UDP
         ↓
┌─────────────────┐
│    Backend      │
│   (FastAPI +    │
│   WebSocket)    │
└────────┬────────┘
         │ WebSocket
         ↓
┌─────────────────┐
│    Frontend     │
│  (HTML/CSS/JS)  │
└─────────────────┘
```

## Project Structure

```
.
├── backend/
│   ├── telemetry_readers/       # Telemetry ingestion modules
│   │   ├── __init__.py
│   │   ├── base_reader.py       # Base class
│   │   ├── acc_reader.py        # ACC shared memory
│   │   ├── r3e_reader.py        # RaceRoom shared memory
│   │   ├── ams2_reader.py       # AMS2 UDP parser
│   │   └── lmu_reader.py        # LMU rF2 shared memory
│   ├── main.py                  # FastAPI server
│   ├── demo_telemetry_generator.py  # Demo mode simulator
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── index.html               # Dashboard UI
│   ├── nginx.conf
│   └── Dockerfile
├── docker-compose.yml
├── TELEMETRY_IMPLEMENTATION.md  # Implementation guide
└── README.md (this file)
```

## Current Status

### ✅ Completed
- [x] Dashboard UI with all telemetry displays
- [x] WebSocket-based real-time communication
- [x] Demo mode with simulated GT3 telemetry
- [x] Telemetry reader architecture and base classes
- [x] Track map visualization (Spa, Monza, Silverstone)
- [x] Tire/brake temperature monitoring with color coding
- [x] THR/BRK horizontal input bars
- [x] RPM display
- [x] Track status with flag indicators

### 🚧 In Progress / TODO
- [ ] **Implement actual telemetry readers** (currently stub implementations)
  - [ ] ACC shared memory reader (use PyAccSharedMemory library)
  - [ ] RaceRoom shared memory reader (implement R3E SDK)
  - [ ] AMS2 UDP parser (Project CARS 2 format)
  - [ ] LMU rF2 shared memory reader
- [ ] Fix brake temperature corruption issue in demo mode
- [ ] Fix tire/brake temp display stopping after a while
- [ ] Implement AI coaching engine with GPT integration
- [ ] Add InfluxDB time-series storage
- [ ] Add Grafana dashboards for historical analysis
- [ ] Add more track layouts

## Installation & Setup

### Prerequisites
- **Windows PC** (for shared memory access to ACC/R3E/LMU)
- Python 3.9+
- Docker & Docker Compose (optional, for containerized deployment)

### Running with Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Access the dashboard at: `http://localhost:8080`

### Running Locally (Development)

#### Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
```

Backend will run on `http://localhost:5001`

#### Frontend
Simply open `frontend/index.html` in a web browser, or serve with:
```bash
cd frontend
python -m http.server 8080
```

## Game-Specific Setup

### ACC (Assetto Corsa Competizione)
- Shared memory is automatically available when ACC is running
- No additional configuration required
- Install `pyaccsharedmemory`: `pip install pyaccsharedmemory`

### RaceRoom (R3E)
- Shared memory is automatically available when R3E is running
- No additional configuration required

### Automobilista 2 (AMS2)
- Enable UDP output in game settings:
  - Options → System → UDP Frequency (set to 60Hz)
  - UDP Port: 9998 (default, configurable)
- Ensure firewall allows UDP on port 9998

### Le Mans Ultimate (LMU)
- Install rFactor 2 Shared Memory Plugin for LMU
- Enable plugin in LMU settings
- Configure output rate in plugin settings

## Configuration

Environment variables (`.env` file):
```bash
# InfluxDB (optional, for time-series storage)
INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=my-token
INFLUXDB_ORG=simracing
INFLUXDB_BUCKET=telemetry

# OpenAI (optional, for AI coaching)
OPENAI_API_KEY=your-key-here
```

## Development

### Adding a New Telemetry Reader

1. Create a new file in `backend/telemetry_readers/`
2. Inherit from `BaseTelemetryReader`
3. Implement `connect()`, `read_telemetry()`, and `disconnect()`
4. Map game telemetry to `UnifiedTelemetryData` format
5. Add to `__init__.py` exports

### Adding a New Track Layout

Edit `frontend/index.html` and add to `TRACK_LAYOUTS` object:

```javascript
TRACK_LAYOUTS['Your Track'] = [
    {x: 0.35, y: 0.85},  // x, y normalized 0.0-1.0
    {x: 0.35, y: 0.80},
    // ... more points
];
```

## Known Issues

1. **Brake temps showing `--°C`**: Backend occasionally sends corrupt values (>1000°C), frontend filters them out
2. **Tire/brake temp display stops**: Investigation needed
3. **Demo mode only**: Real telemetry readers are stub implementations

## References

- [ACC Shared Memory](https://github.com/rrennoir/PyAccSharedMemory)
- [RaceRoom API](https://github.com/sector3studios/r3e-api)
- [rFactor 2 Shared Memory Plugin](https://github.com/TheIronWolfModding/rF2SharedMemoryMapPlugin)
- [Project CARS 2 UDP Format](https://www.projectcarsgame.com/two/api.html)

## License

MIT License

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Session Save Location
- Work-related: `/Users/kltalsma/Wehkamp/AI/`
- Personal: `/Users/kltalsma/Prive/AI/`
