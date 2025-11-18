# Telemetry Implementation Plan

## Overview
Implement real-time telemetry ingestion for 4 racing simulators:
- Assetto Corsa Competizione (ACC)
- RaceRoom Racing Experience (R3E)
- Le Mans Ultimate (LMU)
- Automobilista 2 (AMS2)

## Implementation Strategy

### 1. ACC (Assetto Corsa Competizione)
**Method**: Shared Memory
**Library**: PyAccSharedMemory (https://github.com/rrennoir/PyAccSharedMemory)
**Status**: Found existing library ✓

**Implementation**:
- Read from Windows shared memory mapped files
- ACC provides 3 memory mapped files: Physics, Graphics, Static
- High frequency updates (60Hz+)

**Dependencies**:


### 2. RaceRoom Racing Experience (R3E)
**Method**: Shared Memory
**Documentation**: R3E provides shared memory API
**Status**: Need to implement custom reader

**Implementation**:
- Similar to ACC, uses Windows shared memory
- Memory layout documented in R3E SDK
- Struct-based parsing required

**Dependencies**:


### 3. Automobilista 2 (AMS2)
**Method**: UDP Broadcast
**Format**: Project CARS 2 UDP format
**Status**: Need to implement UDP parser

**Implementation**:
- Listen on UDP port (configurable, default 9998)
- Parse Project CARS 2 telemetry packets
- Multiple packet types (telemetry, race data, etc.)

**Dependencies**:


### 4. Le Mans Ultimate (LMU)
**Method**: Shared Memory (rFactor 2 plugin)
**Format**: rF2 Shared Memory
**Status**: Need to implement rF2 reader

**Implementation**:
- Uses rFactor 2 shared memory plugin
- Similar to R3E, struct-based parsing
- Multiple memory mapped files

**Dependencies**:


## File Structure


## Testing Strategy
1. Test each reader individually with dummy/test data
2. Test on Windows with actual game running
3. Verify all telemetry fields map correctly to UnifiedTelemetry
4. Test performance (should handle 60Hz updates)

## Platform Notes
- **Windows Only**: Shared memory APIs require Windows
- **Docker Limitation**: Cannot access Windows shared memory from Docker Linux containers
- **Deployment**: Must run natively on Windows for real telemetry

## Next Steps
1. ✓ Create directory structure
2. Implement base reader class
3. Implement ACC reader (using PyAccSharedMemory)
4. Implement R3E reader (custom)
5. Implement AMS2 UDP reader
6. Implement LMU/rF2 reader
7. Update main.py to use readers
8. Test on Windows sim racing PC
9. Push to GitHub
