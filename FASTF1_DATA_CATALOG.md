# FastF1 Data Catalog

## Overview
FastF1 provides comprehensive Formula 1 session data from the official F1 live timing API. This document catalogs all available data fields and their potential use cases.

---

## 🏁 Session-Level Data

### Event Metadata
- **EventName**: Grand Prix name (e.g., "Abu Dhabi Grand Prix")
- **EventDate**: Date of the event
- **Location**: Circuit location (e.g., "Yas Island")
- **Country**: Host country
- **OfficialEventName**: Full official event title
- **Circuit**: Track name and configuration

### Session Information
- **Session Type**: FP1, FP2, FP3, Qualifying, Sprint, Race
- **Total Laps**: Total laps completed in session
- **Session Start Time**: Official start time
- **Drivers**: List of participating drivers (20 typically)

---

## 🌤️ Weather Data
**~150-200 records per race session**

### Available Fields
- **Time**: Timestamp during session
- **AirTemp**: Air temperature (°C)
- **TrackTemp**: Track surface temperature (°C)
- **Humidity**: Relative humidity (%)
- **Pressure**: Atmospheric pressure (mbar)
- **Rainfall**: Rainfall indicator (0 or 1)
- **WindSpeed**: Wind speed (m/s)
- **WindDirection**: Wind direction (degrees)

### Use Cases
- Tire strategy analysis (track temp affects grip/degradation)
- Performance correlation (air temp affects engine/downforce)
- Race strategy predictions
- Historical weather pattern analysis

---

## 🏎️ Lap Data
**~1,000-1,200 laps per race (58 laps × 20 drivers)**

### Timing Data
- **LapTime**: Total lap time
- **LapNumber**: Sequential lap number
- **Sector1Time, Sector2Time, Sector3Time**: Individual sector times
- **IsPersonalBest**: Flag for driver's best lap
- **IsAccurate**: Data accuracy flag

### Position & Status
- **Position**: Track position during lap
- **TrackStatus**: Track condition code
  - `1`: Green flag (normal racing)
  - `2`: Yellow flag
  - `4`: Safety car
  - `6`: Virtual safety car (VSC)
- **Deleted**: Lap time deleted (track limits)
- **DeletedReason**: Why lap was invalidated

### Speed Measurements
- **SpeedI1**: Speed at intermediate 1 (km/h)
- **SpeedI2**: Speed at intermediate 2 (km/h)
- **SpeedFL**: Speed at finish line (km/h)
- **SpeedST**: Speed trap measurement (km/h)

### Tire Strategy
- **Compound**: Tire compound (SOFT, MEDIUM, HARD)
- **TyreLife**: Laps completed on current tires
- **FreshTyre**: New tire indicator
- **Stint**: Stint number (1st, 2nd, 3rd set of tires)

### Pit Stop Data
- **PitInTime**: Time entering pit lane
- **PitOutTime**: Time exiting pit lane
- **LapStartTime**: Session time at lap start

### Use Cases
- Tire degradation analysis
- Pace comparison (same compound/stint)
- Pit stop strategy optimization
- Track evolution tracking
- Safety car impact analysis
- Qualifying lap deletions analysis

---

## 🚗 Car Telemetry (Per Lap)
**~600-800 data points per lap (varies by circuit length)**

### Available When Loading `telemetry=True`

#### Engine & Speed
- **RPM**: Engine revolutions per minute
- **Speed**: Current speed (km/h)
- **nGear**: Current gear (1-8)
- **Throttle**: Throttle position (0-100%)
- **Brake**: Brake pressure (0-100+)

#### Aerodynamics
- **DRS**: DRS status
  - `0`: DRS closed
  - `1`: DRS available but not activated
  - `8`: DRS active/open
  - Other codes for detection zones

#### Position & Navigation
- **X, Y, Z**: GPS coordinates on track (meters)
- **Distance**: Distance around track from start line (meters)
- **RelativeDistance**: Normalized distance (0-1)

#### Telemetry Metadata
- **Time**: Elapsed time in lap
- **SessionTime**: Absolute session time
- **Date**: Real-world timestamp
- **Source**: Data source indicator
- **Status**: Driver status (OnTrack, InPit, etc.)

#### Driver Context
- **DriverAhead**: Driver number ahead
- **DistanceToDriverAhead**: Gap to car ahead (meters)

### Use Cases
- Corner-by-corner speed analysis
- Braking point comparison
- Gear selection optimization
- DRS usage patterns
- Overtaking analysis (gap tracking)
- Mini-sector time comparisons
- Racing line visualization (X, Y coordinates)
- Throttle trace analysis
- Energy deployment patterns (via speed/throttle correlation)

---

## 📊 Session Results
**20 records per session (one per driver)**

### Driver Performance
- **FullName**: Driver full name
- **Abbreviation**: 3-letter driver code (VER, HAM, etc.)
- **DriverNumber**: Permanent race number
- **TeamName**: Constructor name
- **TeamColor**: Official team color hex code

### Race/Qualifying Results
- **Position**: Final classification position
- **GridPosition**: Starting grid position (race only)
- **Q1, Q2, Q3**: Qualifying session best times
- **Points**: Championship points awarded
- **Status**: Finish status
  - `Finished`: Completed race
  - `+N Lap`: Lapped by leader
  - `Retired`: DNF with reason
  - `Disqualified`: DSQ

### Additional Metrics
- **ClassifiedPosition**: Official classification
- **Time**: Time behind winner (or total race time)
- **Status**: Detailed finish status

### Use Cases
- Championship standings calculation
- Grid vs finish position analysis
- Team mate comparisons
- DNF/reliability tracking
- Qualifying progression analysis (Q1→Q2→Q3)

---

## 🏁 Race Control Messages
**~80-150 messages per session**

### Message Types
- **Category**:
  - `Flag`: Flag status changes (yellow, red, green)
  - `SafetyCar`: SC/VSC deployment
  - `Drs`: DRS enable/disable
  - `Other`: General race control information

### Message Content
- **Time**: Real-world timestamp
- **Message**: Human-readable message text
- **Flag**: Flag type (if applicable)
- **Sector**: Track sector affected
- **RacingNumber**: Driver involved (if applicable)

### Sample Messages
- "GREEN LIGHT - PIT EXIT OPEN"
- "DRS ENABLED"
- "DOUBLE YELLOW IN TRACK SECTOR 14"
- "RISK OF RAIN FOR F1 RACE IS 0%"

### Use Cases
- Incident timeline reconstruction
- Safety car period analysis
- DRS window tracking
- Yellow flag impact on lap times
- Penalty tracking

---

## 📍 Position Data (Per Driver)
**~30,000-35,000 records per race per driver**

### Real-Time Position
- **Date**: Timestamp
- **SessionTime**: Elapsed session time
- **Status**: Driver status (OnTrack, InPit)
- **X, Y, Z**: GPS coordinates
- **Source**: Data source

### Use Cases
- Race visualization/animation
- Battle analysis (side-by-side positioning)
- Pit stop timing optimization
- Position change tracking over time

---

## 🎯 Car Data (Per Driver)
**~30,000-35,000 records per race per driver**

### Continuous Stream Data
- **RPM**: Engine RPM
- **Speed**: Current speed
- **nGear**: Gear selection
- **Throttle**: Throttle application
- **Brake**: Brake pressure
- **DRS**: DRS status

Same as telemetry but as continuous time-series rather than per-lap basis.

### Use Cases
- Full race throttle/brake trace
- Fuel saving behavior analysis
- Consistent performance tracking
- Tire management patterns

---

## ⏱️ Session Status
**Event-driven records throughout session**

### Status Changes
- **Time**: Session time
- **Status**: Session state
  - `Started`: Session began
  - `Aborted`: Red flag
  - `Finished`: Session ended
  - `Finalized`: Official results confirmed

### Use Cases
- Session interruption tracking
- Red flag period identification
- Official result timing

---

## 🚦 Track Status
**Event-driven records for flag changes**

### Track Conditions
- **Time**: When status changed
- **Status**: Track status code (1-7)
- **Message**: Human-readable status

### Use Cases
- Yellow flag period analysis
- Safety car lap identification
- VSC lap time adjustments

---

## ❌ Data NOT Available in FastF1

### Technical Restrictions
- **Car Upgrades**: No component/package information
- **Fuel Load**: Not disclosed
- **Tire Pressure/Temperature**: Internal tire data
- **Aerodynamic Settings**: Wing angles, ride height
- **Engine Modes**: Power unit deployment settings
- **Brake Temperatures**: Caliper/disc temperatures

### Media/Communications
- **Team Radio**: No audio or transcripts
- **Driver Biometrics**: No heart rate, g-forces felt
- **Onboard Video**: No video data

### Business/Financial
- **Cost Cap Data**: No financial information
- **Contract Details**: No driver/team agreements
- **Development Budgets**: No R&D spend data

---

## 📦 Current Implementation Status

### ✅ Currently Stored in Warehouse
- Lap times and sector times
- Session results (positions, points)
- Tire compounds and strategy
- Pit stop data
- Basic session metadata

### 🟡 Available but Not Yet Stored
- **Weather data** (track/air temp, humidity, wind)
- **Car telemetry** (speed, throttle, brake, RPM, DRS)
- **Position data** (GPS coordinates, real-time tracking)
- **Race control messages** (flags, incidents)
- **Track status** (yellow flags, safety car periods)
- **Speed trap data** (I1, I2, FL, ST speeds)

### 🚀 Potential Enhancements
1. **Weather Schema**: Add weather table with temperature, humidity, wind
2. **Telemetry Tables**: Store speed traces, throttle/brake data per lap
3. **Position Tracking**: GPS coordinates for race visualization
4. **Race Control**: Flag periods, incidents, penalties
5. **Speed Analysis**: Speed trap comparisons, sector speed analysis

---

## 💡 High-Value Data Use Cases

### For Fans
- **Tire Strategy**: See compound choices and degradation
- **Battle Analysis**: Compare telemetry during overtakes
- **Weather Impact**: Correlate performance with conditions
- **Safety Car**: Analyze strategy calls during SC periods

### For Analysis
- **Performance Trends**: Weather-adjusted pace analysis
- **Reliability**: Track DNF patterns and causes
- **Pit Strategy**: Optimal pit window identification
- **Qualifying**: Sector-by-sector improvement tracking

### For Visualization
- **Race Replay**: Animate positions using GPS data
- **Speed Maps**: Overlay speed on track layout
- **Telemetry Comparison**: Side-by-side driver traces
- **Weather Dashboard**: Conditions throughout weekend

---

## 🔧 Next Steps

### Quick Wins
1. Add weather table to warehouse
2. Export speed trap data (already in laps)
3. Store race control messages
4. Add track status indicators

### Advanced Features
1. Telemetry storage (large volume - consider sampling)
2. Position data for race visualization
3. Mini-sector analysis (requires telemetry)
4. Real-time data ingestion (for live sessions)

### Storage Considerations
- **Weather**: ~150 rows/session = minimal storage
- **Race Control**: ~100 rows/session = minimal storage  
- **Telemetry**: ~600 points/lap × 1200 laps = ~720K rows/race (larger)
- **Position Data**: ~35K points/driver × 20 drivers = ~700K rows/race (larger)

**Recommendation**: Start with weather and race control (low storage), then evaluate telemetry sampling strategies for advanced analysis.
