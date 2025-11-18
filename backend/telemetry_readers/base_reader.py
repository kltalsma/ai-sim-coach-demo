"""
Base class for all telemetry readers
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import asyncio


@dataclass
class UnifiedTelemetryData:
    """Unified telemetry data structure"""
    # Basic
    speed: float  # km/h
    rpm: int
    gear: int
    max_rpm: int
    
    # Position
    lap_distance: float  # 0.0 to 1.0
    lap_time: float  # seconds
    lap_number: int
    last_lap_time: float
    best_lap_time: float
    
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
    fuel: float  # Liters
    fuel_laps: int
    
    # Electronics
    tc: int
    abs: int
    brake_bias: float
    engine_map: int
    
    # Race Position
    position: int
    total_cars: int
    
    # Session
    session_type: str
    session_time_remaining: float
    track_name: str
    car_name: str
    
    # Sector Deltas (optional)
    sector_1_delta: Optional[float] = None
    sector_2_delta: Optional[float] = None
    sector_3_delta: Optional[float] = None


class BaseTelemetryReader(ABC):
    """Base class for all telemetry readers"""
    
    def __init__(self):
        self.running = False
        self.latest_data: Optional[UnifiedTelemetryData] = None
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        Connect to telemetry source
        Returns True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def read_telemetry(self) -> Optional[UnifiedTelemetryData]:
        """
        Read telemetry data
        Returns UnifiedTelemetryData if successful, None otherwise
        """
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Disconnect from telemetry source"""
        pass
    
    async def start(self, callback):
        """
        Start reading telemetry and call callback with each update
        
        Args:
            callback: Async function to call with telemetry data
        """
        self.running = True
        
        if not await self.connect():
            print(f"{self.__class__.__name__}: Failed to connect")
            return
        
        print(f"{self.__class__.__name__}: Connected")
        
        try:
            while self.running:
                data = await self.read_telemetry()
                if data:
                    self.latest_data = data
                    await callback(data)
                await asyncio.sleep(0.016)  # ~60 FPS
        finally:
            await self.disconnect()
            print(f"{self.__class__.__name__}: Disconnected")
    
    async def stop(self):
        """Stop reading telemetry"""
        self.running = False
