"""
AI Sim Racing Coach - Backend Server
Supports: ACC, RaceRoom, Le Mans Ultimate, Automobilista 2
"""

import asyncio
import json
import struct
import time
from datetime import datetime
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import uvicorn
from dotenv import load_dotenv
import os

load_dotenv()

# Configuration
UDP_PORT_ACC = 9996  # Assetto Corsa Competizione
UDP_PORT_R3E = 9997  # RaceRoom Racing Experience
UDP_PORT_AMS2 = 9998  # Automobilista 2 (Project CARS format)
UDP_PORT_LMU = 9999  # Le Mans Ultimate (rF2 format)
WEBSOCKET_PORT = 5001

# Demo mode control
demo_task = None
demo_running = False
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "my-token")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "simracing")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "telemetry")


class GameType(Enum):
    ACC = "Assetto Corsa Competizione"
    R3E = "RaceRoom Racing Experience"
    AMS2 = "Automobilista 2"
    LMU = "Le Mans Ultimate"
    DEMO = "Demo Mode"


@dataclass
class UnifiedTelemetry:
    """Unified telemetry format for all sims"""
    timestamp: float
    game: str
    
    # Basic
    speed: float  # km/h
    rpm: int
    gear: int
    max_rpm: int
    
    # Position
    lap_distance: float  # 0.0 to 1.0
    lap_time: float  # seconds (current lap time)
    lap_number: int
    last_lap_time: float
    best_lap_time: float
    current_lap_time: float  # Alias for lap_time for frontend
    
    # Inputs
    throttle: float  # 0.0 to 1.0
    brake: float
    clutch: float
    steering: float  # -1.0 to 1.0
    
    # Forces
    g_force_lateral: float
    g_force_longitudinal: float
    g_force_vertical: float
    
    # Tires (FL, FR, RL, RR)
    tire_temp_fl: float
    tire_temp_fr: float
    tire_temp_rl: float
    tire_temp_rr: float
    
    tire_pressure_fl: float
    tire_pressure_fr: float
    tire_pressure_rl: float
    tire_pressure_rr: float
    
    # Brakes
    brake_temp_fl: float
    brake_temp_fr: float
    brake_temp_rl: float
    brake_temp_rr: float
    
    # Engine/Fuel
    oil_temp: float
    water_temp: float
    fuel_level: float  # 0.0 to 1.0
    fuel: float  # Liters remaining
    fuel_laps: int  # Estimated laps remaining
    
    # Electronics
    tc: int  # Traction control level
    abs: int  # ABS level
    brake_bias: float  # 0.0 to 1.0
    engine_map: int  # Engine map selection
    
    # Race Position
    position: int
    total_cars: int
    
    # Session
    session_type: str
    session_time_remaining: float  # seconds
    track_name: str
    car_name: str
    
    # Sector Deltas
    sector_1_delta: Optional[float]
    sector_2_delta: Optional[float]
    sector_3_delta: Optional[float]
    
    # Leaderboard
    leaderboard: Optional[List[Dict]]
    
    # AI Coaching
    coaching_messages: List[str]
    coaching_message: Optional[str]  # Latest message


class CoachingEngine:
    """Real-time coaching rules engine"""
    
    @staticmethod
    def analyze(telemetry: UnifiedTelemetry) -> List[str]:
        """Generate coaching messages based on telemetry"""
        messages = []
        
        # Tire temperature analysis
        tire_temps = [
            telemetry.tire_temp_fl,
            telemetry.tire_temp_fr,
            telemetry.tire_temp_rl,
            telemetry.tire_temp_rr
        ]
        avg_tire_temp = sum(tire_temps) / len(tire_temps)
        temp_variance = max(tire_temps) - min(tire_temps)
        
        if avg_tire_temp > 105:
            messages.append("⚠️ TIRE OVERHEAT: Tires above optimal range (105°C+)")
        elif avg_tire_temp < 70:
            messages.append("❄️ Cold tires: Push harder to build temperature (optimal: 80-95°C)")
        
        if temp_variance > 15:
            messages.append(f"⚖️ Tire imbalance: {temp_variance:.1f}°C difference detected")
        
        # Brake temperature
        brake_temps = [
            telemetry.brake_temp_fl,
            telemetry.brake_temp_fr,
            telemetry.brake_temp_rl,
            telemetry.brake_temp_rr
        ]
        avg_brake_temp = sum(brake_temps) / len(brake_temps)
        
        if avg_brake_temp > 800:
            messages.append("🔥 CRITICAL: Brake fade risk! Reduce brake pressure")
        elif avg_brake_temp > 650:
            messages.append("⚠️ High brake temps: Consider cooling lap")
        
        # Fuel management
        if telemetry.fuel_level < 0.15:
            laps_remaining = int(telemetry.fuel_level * 50)  # Estimate
            messages.append(f"⛽ LOW FUEL: ~{laps_remaining} laps remaining")
        
        # Driving technique
        if telemetry.throttle > 0.2 and telemetry.brake > 0.2:
            messages.append("⚠️ Brake/throttle overlap detected - trail braking or technique issue?")
        
        # RPM management
        if telemetry.rpm > telemetry.max_rpm * 0.95:
            messages.append("🔴 RPM LIMIT: Shift up!")
        
        # G-force analysis
        if abs(telemetry.g_force_lateral) > 2.5:
            messages.append(f"💨 High lateral G: {abs(telemetry.g_force_lateral):.2f}g")
        
        # Lap time comparison
        if telemetry.best_lap_time < 999 and telemetry.lap_time > 0:
            delta = telemetry.lap_time - (telemetry.best_lap_time * telemetry.lap_distance)
            if abs(delta) > 0.5:
                sign = "+" if delta > 0 else ""
                messages.append(f"📊 Delta: {sign}{delta:.3f}s")
        
        return messages


class TelemetryHub:
    """Central hub for telemetry distribution"""
    
    def __init__(self):
        self.websocket_clients: Set[WebSocket] = set()
        self.latest_telemetry: Optional[UnifiedTelemetry] = None
        self.influx_client = None
        self.write_api = None
        
        # Initialize InfluxDB
        try:
            self.influx_client = InfluxDBClient(
                url=INFLUXDB_URL,
                token=INFLUXDB_TOKEN,
                org=INFLUXDB_ORG
            )
            self.write_api = self.influx_client.write_api(write_options=SYNCHRONOUS)
            print(f"✓ Connected to InfluxDB at {INFLUXDB_URL}")
        except Exception as e:
            print(f"⚠️ InfluxDB not available: {e}")
    
    async def broadcast_telemetry(self, telemetry: UnifiedTelemetry):
        """Broadcast telemetry to WebSocket clients and InfluxDB"""
        self.latest_telemetry = telemetry
        
        # Add coaching messages
        telemetry.coaching_messages = CoachingEngine.analyze(telemetry)
        
        # Broadcast to WebSocket clients
        data = json.dumps(asdict(telemetry))
        disconnected = set()
        
        # Iterate over a copy to avoid "set changed size during iteration" error
        for client in list(self.websocket_clients):
            try:
                await client.send_text(data)
            except Exception:
                disconnected.add(client)
        
        # Remove disconnected clients
        self.websocket_clients -= disconnected
        
        # Write to InfluxDB
        if self.write_api:
            try:
                point = Point("telemetry") \
                    .tag("game", telemetry.game) \
                    .tag("session_type", telemetry.session_type) \
                    .tag("track", telemetry.track_name) \
                    .tag("car", telemetry.car_name) \
                    .field("speed", telemetry.speed) \
                    .field("rpm", telemetry.rpm) \
                    .field("gear", telemetry.gear) \
                    .field("throttle", telemetry.throttle) \
                    .field("brake", telemetry.brake) \
                    .field("steering", telemetry.steering) \
                    .field("tire_temp_fl", telemetry.tire_temp_fl) \
                    .field("tire_temp_fr", telemetry.tire_temp_fr) \
                    .field("tire_temp_rl", telemetry.tire_temp_rl) \
                    .field("tire_temp_rr", telemetry.tire_temp_rr) \
                    .field("tire_pressure_fl", telemetry.tire_pressure_fl) \
                    .field("tire_pressure_fr", telemetry.tire_pressure_fr) \
                    .field("tire_pressure_rl", telemetry.tire_pressure_rl) \
                    .field("tire_pressure_rr", telemetry.tire_pressure_rr) \
                    .field("brake_temp_fl", telemetry.brake_temp_fl) \
                    .field("brake_temp_fr", telemetry.brake_temp_fr) \
                    .field("brake_temp_rl", telemetry.brake_temp_rl) \
                    .field("brake_temp_rr", telemetry.brake_temp_rr) \
                    .field("g_lateral", telemetry.g_force_lateral) \
                    .field("g_longitudinal", telemetry.g_force_longitudinal) \
                    .field("fuel_level", telemetry.fuel_level) \
                    .field("lap_time", telemetry.lap_time) \
                    .field("lap_distance", telemetry.lap_distance) \
                    .time(datetime.utcnow())
                
                self.write_api.write(bucket=INFLUXDB_BUCKET, record=point)
            except Exception as e:
                print(f"InfluxDB write error: {e}")
    
    def add_websocket_client(self, websocket: WebSocket):
        """Add WebSocket client"""
        self.websocket_clients.add(websocket)
    
    def remove_websocket_client(self, websocket: WebSocket):
        """Remove WebSocket client"""
        self.websocket_clients.discard(websocket)


# Global telemetry hub
telemetry_hub = TelemetryHub()

# FastAPI app
app = FastAPI(title="AI Sim Racing Coach API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time telemetry"""
    await websocket.accept()
    telemetry_hub.add_websocket_client(websocket)
    
    try:
        # Send initial data if available
        if telemetry_hub.latest_telemetry:
            await websocket.send_text(json.dumps(asdict(telemetry_hub.latest_telemetry)))
        
        # Keep connection alive
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        telemetry_hub.remove_websocket_client(websocket)


@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "running",
        "service": "AI Sim Racing Coach",
        "games_supported": [g.value for g in GameType],
        "websocket_clients": len(telemetry_hub.websocket_clients),
        "latest_telemetry": telemetry_hub.latest_telemetry is not None
    }


@app.get("/api/status")
async def status():
    """System status"""
    return {
        "udp_ports": {
            "ACC": UDP_PORT_ACC,
            "RaceRoom": UDP_PORT_R3E,
            "AMS2": UDP_PORT_AMS2,
            "LMU": UDP_PORT_LMU
        },
        "websocket_port": WEBSOCKET_PORT,
        "connected_clients": len(telemetry_hub.websocket_clients),
        "influxdb_connected": telemetry_hub.influx_client is not None,
        "last_update": telemetry_hub.latest_telemetry.timestamp if telemetry_hub.latest_telemetry else None,
        "demo_running": demo_running
    }


@app.post("/demo/start")
async def start_demo():
    """Start demo mode"""
    global demo_task, demo_running
    if not demo_running:
        demo_running = True
        demo_task = asyncio.create_task(demo_mode())
        return {"status": "started", "message": "Demo mode started"}
    return {"status": "already_running", "message": "Demo mode already running"}


@app.post("/demo/stop")
async def stop_demo():
    """Stop demo mode"""
    global demo_task, demo_running
    if demo_running:
        demo_running = False
        if demo_task:
            demo_task.cancel()
            try:
                await demo_task
            except asyncio.CancelledError:
                pass
        return {"status": "stopped", "message": "Demo mode stopped"}
    return {"status": "already_stopped", "message": "Demo mode already stopped"}


async def udp_receiver_acc():
    """UDP receiver for Assetto Corsa Competizione"""
    # TODO: Implement ACC shared memory reader
    # ACC uses shared memory, not UDP
    print(f"ACC receiver: Use shared memory interface (not UDP)")
    pass


async def udp_receiver_r3e():
    """UDP receiver for RaceRoom Racing Experience"""
    # TODO: Implement R3E shared memory reader
    print(f"RaceRoom receiver: Use shared memory interface (not UDP)")
    pass


async def udp_receiver_ams2():
    """UDP receiver for Automobilista 2"""
    # TODO: Implement AMS2 UDP parser (Project CARS format)
    print(f"Listening for AMS2 telemetry on UDP port {UDP_PORT_AMS2}")
    pass


async def udp_receiver_lmu():
    """UDP receiver for Le Mans Ultimate"""
    # TODO: Implement LMU shared memory reader (rF2 format)
    print(f"LMU receiver: Use rF2 shared memory plugin")
    pass


async def demo_mode():
    """Demo mode with simulated telemetry"""
    global demo_running
    print("🎮 Starting DEMO mode with simulated telemetry")
    
    from demo_telemetry_generator import GT3TelemetrySimulator
    
    simulator = GT3TelemetrySimulator()
    
    while demo_running:
        frame = simulator.generate_frame()
        
        # Convert to unified format
        unified = UnifiedTelemetry(
            timestamp=frame.timestamp,
            game=GameType.DEMO.value,
            speed=frame.speed,
            rpm=frame.rpm,
            gear=frame.gear,
            max_rpm=frame.max_rpm,
            lap_distance=frame.lap_distance,
            lap_time=frame.lap_time,
            lap_number=frame.lap_number,
            last_lap_time=frame.last_lap_time,
            best_lap_time=frame.best_lap_time,
            current_lap_time=frame.lap_time,  # Alias for frontend
            throttle=frame.throttle,
            brake=frame.brake,
            clutch=frame.clutch,
            steering=frame.steering,
            g_force_lateral=frame.g_force_lateral,
            g_force_longitudinal=frame.g_force_longitudinal,
            g_force_vertical=frame.g_force_vertical,
            tire_temp_fl=frame.tire_temp_fl,
            tire_temp_fr=frame.tire_temp_fr,
            tire_temp_rl=frame.tire_temp_rl,
            tire_temp_rr=frame.tire_temp_rr,
            tire_pressure_fl=frame.tire_pressure_fl,
            tire_pressure_fr=frame.tire_pressure_fr,
            tire_pressure_rl=frame.tire_pressure_rl,
            tire_pressure_rr=frame.tire_pressure_rr,
            brake_temp_fl=frame.brake_temp_fl,
            brake_temp_fr=frame.brake_temp_fr,
            brake_temp_rl=frame.brake_temp_rl,
            brake_temp_rr=frame.brake_temp_rr,
            oil_temp=frame.oil_temp,
            water_temp=frame.water_temp,
            fuel_level=frame.fuel_level,
            fuel=frame.fuel_level * 120.0,  # Convert percentage to liters (120L tank)
            fuel_laps=int(frame.fuel_remaining_laps),
            tc=2,  # Traction control level
            abs=3,  # ABS level
            brake_bias=0.56,  # 56% front
            engine_map=1,  # Engine map 1
            position=1 + (simulator.lap_number % 3),  # Simulate position changes 1-3
            total_cars=20,  # 20 car grid
            session_type=frame.session_type,
            session_time_remaining=1800.0 - (simulator.lap_time + (simulator.lap_number - 1) * 150.0),  # 30 min session
            track_name="Spa-Francorchamps",
            car_name="Mercedes-AMG GT3",
            sector_1_delta=-0.234 if simulator.best_lap_time < 999 else None,
            sector_2_delta=0.156 if simulator.best_lap_time < 999 else None,
            sector_3_delta=-0.089 if simulator.best_lap_time < 999 else None,
            leaderboard=[
                {"position": 1, "car_number": "77", "driver_name": "You", "gap": "LEAD", "best_lap": simulator.best_lap_time if simulator.best_lap_time < 999 else None, "sector_1": 30.234, "sector_2": 48.567, "sector_3": 28.123},
                {"position": 2, "car_number": "33", "driver_name": "M. Verstappen", "gap": "+2.345", "best_lap": simulator.best_lap_time + 0.234 if simulator.best_lap_time < 999 else None, "sector_1": 30.345, "sector_2": 48.678, "sector_3": 28.234},
                {"position": 3, "car_number": "44", "driver_name": "L. Hamilton", "gap": "+5.678", "best_lap": simulator.best_lap_time + 0.567 if simulator.best_lap_time < 999 else None, "sector_1": 30.456, "sector_2": 48.789, "sector_3": 28.345},
                {"position": 4, "car_number": "16", "driver_name": "C. Leclerc", "gap": "+8.912", "best_lap": simulator.best_lap_time + 0.891 if simulator.best_lap_time < 999 else None, "sector_1": 30.567, "sector_2": 48.890, "sector_3": 28.456},
                {"position": 5, "car_number": "55", "driver_name": "C. Sainz", "gap": "+12.234", "best_lap": simulator.best_lap_time + 1.234 if simulator.best_lap_time < 999 else None, "sector_1": 30.678, "sector_2": 48.901, "sector_3": 28.567},
            ],
            coaching_messages=[],
            coaching_message=None  # Will be set by CoachingEngine
        )
        
        await telemetry_hub.broadcast_telemetry(unified)
        await asyncio.sleep(0.016)  # 60 FPS


@app.on_event("startup")
async def startup_event():
    """Start background tasks"""
    global demo_task, demo_running
    # Start UDP receivers for all supported games
    asyncio.create_task(udp_receiver_acc())
    asyncio.create_task(udp_receiver_r3e())
    asyncio.create_task(udp_receiver_ams2())
    asyncio.create_task(udp_receiver_lmu())
    
    # Start demo mode (will auto-stop when real telemetry arrives)
    demo_running = True
    demo_task = asyncio.create_task(demo_mode())
    
    print("=" * 80)
    print("🏁 AI Sim Racing Coach - Backend Started")
    print("=" * 80)
    print(f"WebSocket: ws://localhost:{WEBSOCKET_PORT}/ws")
    print(f"API: http://localhost:{WEBSOCKET_PORT}")
    print(f"Supported Games: ACC, RaceRoom, LMU, Automobilista 2")
    print("=" * 80)


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=WEBSOCKET_PORT,
        log_level="info"
    )
