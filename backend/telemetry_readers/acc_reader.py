"""
Assetto Corsa Competizione (ACC) Telemetry Reader
Uses pyaccsharedmemory library to read telemetry from ACC
"""

import platform
from typing import Optional
from .base_reader import BaseTelemetryReader, UnifiedTelemetryData

try:
    from pyaccsharedmemory import accSharedMemory
    ACC_AVAILABLE = True
except ImportError:
    ACC_AVAILABLE = False
    print("WARNING: pyaccsharedmemory not installed. Run: pip install pyaccsharedmemory")


class ACCReader(BaseTelemetryReader):
    """
    ACC telemetry reader using shared memory via pyaccsharedmemory library
    
    ACC exposes 3 shared memory regions:
    - Physics: Real-time physics data (position, speed, forces, etc.)
    - Graphics: HUD/UI related data (lap times, position, etc.)
    - Static: Static car/track information
    """
    
    def __init__(self):
        super().__init__()
        self.asm = None
        self.is_windows = platform.system() == "Windows"
    
    async def connect(self) -> bool:
        """Connect to ACC shared memory"""
        if not self.is_windows:
            print("ACC Reader: Shared memory only available on Windows")
            return False
        
        if not ACC_AVAILABLE:
            print("ACC Reader: pyaccsharedmemory library not installed")
            return False
        
        try:
            print("ACC Reader: Attempting to connect to ACC shared memory...")
            self.asm = accSharedMemory()
            
            # Try to read once to verify connection
            physics = self.asm.ReadPhysics()
            if physics is None:
                print("ACC Reader: ACC not running or shared memory not available")
                return False
            
            print("ACC Reader: Successfully connected to ACC")
            return True
            
        except Exception as e:
            print(f"ACC Reader: Failed to connect: {e}")
            return False
    
    async def read_telemetry(self) -> Optional[UnifiedTelemetryData]:
        """Read telemetry from ACC shared memory"""
        if not self.asm:
            return None
        
        try:
            # Read all three memory regions
            physics = self.asm.ReadPhysics()
            graphics = self.asm.ReadGraphics()
            static = self.asm.ReadStatic()
            
            if not physics or not graphics or not static:
                return None
            
            # Convert ACC data to unified format
            # Note: ACC uses metric (m/s for speed, celsius for temps)
            return UnifiedTelemetryData(
                # Basic
                speed=physics.SpeedKmh,
                rpm=physics.Rpms,
                gear=physics.Gear - 1,  # ACC: 0=R, 1=N, 2=1st, etc. We want: -1=R, 0=N, 1=1st
                max_rpm=static.MaxRpm,
                
                # Position
                lap_distance=graphics.NormalizedCarPosition,
                lap_time=graphics.iCurrentTime / 1000.0,  # ms to seconds
                lap_number=graphics.CompletedLaps + 1,
                last_lap_time=graphics.iLastTime / 1000.0,
                best_lap_time=graphics.iBestTime / 1000.0,
                
                # Inputs
                throttle=physics.Gas,
                brake=physics.Brake,
                clutch=physics.Clutch,
                steering=physics.SteerAngle,
                
                # Forces (ACC provides G-forces directly)
                g_force_lateral=physics.AccG[0],  # X-axis
                g_force_longitudinal=physics.AccG[1],  # Y-axis  
                g_force_vertical=physics.AccG[2],  # Z-axis
                
                # Tire Temps (core temp in Celsius)
                tire_temp_fl=physics.TyreCoreTemp[0],
                tire_temp_fr=physics.TyreCoreTemp[1],
                tire_temp_rl=physics.TyreCoreTemp[2],
                tire_temp_rr=physics.TyreCoreTemp[3],
                
                # Tire Pressure (PSI)
                tire_pressure_fl=physics.WheelPressure[0],
                tire_pressure_fr=physics.WheelPressure[1],
                tire_pressure_rl=physics.WheelPressure[2],
                tire_pressure_rr=physics.WheelPressure[3],
                
                # Brake Temps (Celsius)
                brake_temp_fl=physics.BrakeTemp[0],
                brake_temp_fr=physics.BrakeTemp[1],
                brake_temp_rl=physics.BrakeTemp[2],
                brake_temp_rr=physics.BrakeTemp[3],
                
                # Engine/Fuel
                oil_temp=physics.OilTemp,
                water_temp=physics.WaterTemp,
                fuel_level=physics.Fuel / static.MaxFuel if static.MaxFuel > 0 else 0,
                fuel=physics.Fuel,
                fuel_laps=0,  # ACC doesn't provide this directly
                
                # Electronics
                tc=graphics.TC,
                abs=graphics.ABS,
                brake_bias=physics.BrakeBias,
                engine_map=graphics.EngineMap,
                
                # Race Position
                position=graphics.Position,
                total_cars=static.NumCars,
                
                # Session
                session_type=self._get_session_type(graphics.Session),
                session_time_remaining=graphics.SessionTimeLeft / 1000.0,  # ms to seconds
                track_name=static.Track,
                car_name=static.CarModel,
                
                # Sector Deltas (not available in ACC shared memory)
                sector_1_delta=None,
                sector_2_delta=None,
                sector_3_delta=None,
            )
            
        except Exception as e:
            print(f"ACC Reader: Error reading telemetry: {e}")
            return None
    
    def _get_session_type(self, session_code: int) -> str:
        """Convert ACC session code to readable string"""
        session_types = {
            0: "Practice",
            1: "Qualifying", 
            2: "Race",
            3: "Hotlap",
            4: "Time Attack",
            5: "Drift",
            6: "Drag",
            7: "Hotstint",
            8: "Hotlap Superpole"
        }
        return session_types.get(session_code, "Unknown")
    
    async def disconnect(self):
        """Disconnect from ACC shared memory"""
        if self.asm:
            self.asm = None
            print("ACC Reader: Disconnected")
