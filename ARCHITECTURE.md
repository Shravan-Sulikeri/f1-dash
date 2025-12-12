# F1 ML Pipeline - Complete Data Flow & Architecture

## 📊 End-to-End Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                         RAW DATA SOURCES (2018-2025)                        │
│                                                                             │
│  FastF1 Parquet Files:                                                      │
│  ├─ session_result/     → Race results, grid, finish positions              │
│  ├─ weather/            → Temperature, humidity, wind, pressure, rainfall   │
│  └─ laps/               → Lap-by-lap telemetry (speed, position, etc)      │
│                                                                             │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │
                               ↓
           ╔═══════════════════════════════════════╗
           ║   BRONZE LAYER (Raw Ingestion)        ║
           ║   build_bronze_fastf1_ml.py           ║
           ╚═══════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│                          BRONZE_FASTF1 (Raw)                                │
│                                                                             │
│  ✓ session_result (9,779 rows)                                              │
│    - Season, round, driver, team, grid position, finish position            │
│    - Points scored, DNF status                                              │
│                                                                             │
│  ✓ weather (31,776 rows)                                                    │
│    - Air temperature, track temperature, humidity                           │
│    - Wind speed, wind direction, pressure, rainfall                         │
│    - Time series data per session                                           │
│                                                                             │
│  ✓ laps (221,938 rows)                                                      │
│    - Lap-by-lap telemetry, lap duration, tire compound                      │
│    - Driver number, accuracy flag                                           │
│                                                                             │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │
                               ↓
           ╔═══════════════════════════════════════╗
           ║   SILVER LAYER (Aggregation)          ║
           ║   build_silver_fastf1_ml.py           ║
           ╚═══════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│                        SILVER_FASTF1 (Aggregated)                           │
│                                                                             │
│  ✓ race_data (3,175 rows)                                                   │
│    ├─ Base race info + weather aggregates (avg, max, min)                   │
│    ├─ Weather flags: is_wet_race, is_high_humidity                          │
│    └─ Targets: target_win, target_podium, target_finish                     │
│                                                                             │
│  ✓ driver_career_stats (43 drivers)                                         │
│    ├─ Career wins, podiums, races finished                                  │
│    ├─ Average finishing position                                            │
│    └─ Win rate, podium rate, position gain/loss                             │
│                                                                             │
│  ✓ driver_venue_stats (1,159 records)                                       │
│    ├─ Per-driver, per-venue statistics                                      │
│    ├─ Wins, podiums, avg finish at each track                               │
│    └─ Average grid position, point accumulation per venue                   │
│                                                                             │
│  ✓ driver_weather_stats (43 records)                                        │
│    ├─ Dry condition: races, wins, avg finish                                │
│    ├─ Wet condition: races, wins, avg finish                                │
│    └─ Humid condition: races, avg finish                                    │
│                                                                             │
│  ✓ team_stats (22 teams)                                                    │
│    ├─ Team wins, podiums, total points                                      │
│    └─ Average team finishing position                                       │
│                                                                             │
│  ✓ driver_season_form (3,175 rows)                                          │
│    ├─ Rolling 5-race average finishing position                             │
│    ├─ Points accumulated in last 5 races                                    │
│    └─ Average grid position in last 5 races                                 │
│                                                                             │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │
                               ↓
           ╔═══════════════════════════════════════╗
           ║   GOLD LAYER (Feature Engineering)    ║
           ║   build_gold_fastf1_ml.py             ║
           ╚═══════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│                       GOLD_FASTF1 (ML Ready)                                │
│                                                                             │
│  ✓ race_prediction_features (3,175 rows × 61 features)                      │
│                                                                             │
│    WEATHER FEATURES (13)                                                    │
│    ├─ Raw: air temp, track temp, humidity, wind, rainfall, pressure        │
│    ├─ Aggregates: is_wet_race, is_high_humidity                             │
│    └─ Normalized: norm_track_temp, norm_humidity, norm_wind_speed           │
│                                                                             │
│    DRIVER CAREER (8)                                                        │
│    ├─ career_wins, career_podiums, career_races                             │
│    ├─ avg_finish_position, finish_rate, avg_position_gain                   │
│    └─ career_win_pct, career_podium_pct                                     │
│                                                                             │
│    VENUE PERFORMANCE (9)                                                    │
│    ├─ races_at_venue, wins_at_venue, podiums_at_venue                       │
│    ├─ avg_finish_at_venue, avg_grid_at_venue, avg_points_at_venue           │
│    ├─ win_pct_at_venue, podium_pct_at_venue                                 │
│    └─ ever_raced_wet_at_venue                                               │
│                                                                             │
│    SEASON FORM (3)                                                          │
│    ├─ avg_finish_last_5, points_last_5                                      │
│    └─ avg_grid_last_5                                                       │
│                                                                             │
│    TEAM PERFORMANCE (4)                                                     │
│    ├─ team_wins_history, team_podiums_history                               │
│    ├─ team_points_history, team_avg_finish                                  │
│                                                                             │
│    WEATHER ADAPTATION (10)                                                  │
│    ├─ Dry: races, wins, avg_finish, win_pct                                 │
│    ├─ Wet: races, wins, avg_finish, win_pct                                 │
│    └─ Humid: races, avg_finish                                              │
│                                                                             │
│    COMPUTED INDICATORS (5)                                                  │
│    ├─ grid_deviation_from_venue_avg                                         │
│    └─ Normalized weather features                                           │
│                                                                             │
│    TARGET VARIABLES (3)                                                     │
│    ├─ target_win (binary: 1/0)                                              │
│    ├─ target_podium (binary: 1/0)                                           │
│    └─ target_finish (binary: 1/0)                                           │
│                                                                             │
│  ✓ win_prediction_dataset (3,175 rows)                                      │
│    └─ Curated for winner prediction (target_finish=1)                       │
│                                                                             │
│  ✓ podium_prediction_dataset (3,175 rows)                                   │
│    └─ Curated for podium prediction (target_finish=1)                       │
│                                                                             │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │
                               ↓
           ╔═══════════════════════════════════════╗
           ║      MODEL TRAINING                   ║
           ║   train_fastf1_models.py              ║
           ║                                       ║
           ║  Data Split:                          ║
           ║  - Train: 2018-2022 (1,798 rows)      ║
           ║  - Val: 2023 (439 rows)               ║
           ║  - Test: 2024 (479 rows)              ║
           ║  - Holdout: 2025 (459 rows)           ║
           ╚═══════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│                      TRAINED MODELS (ML Artifacts)                          │
│                                                                             │
│  🏆 race_win_rf.joblib (Random Forest)                                      │
│     └─ Predicts race winner                                                 │
│        • Validation AUC: 0.9742                                             │
│        • Test AUC: 0.9907                                                   │
│        • Hit@1: 50% (top prediction wins 50% of races)                      │
│        • Hit@3: 100% (top 3 always contain winner)                          │
│                                                                             │
│  🥇 race_podium_logreg.joblib (Logistic Regression)                         │
│     └─ Predicts podium finish (top 3)                                       │
│        • Validation AUC: 0.9328                                             │
│        • Test AUC: 0.9747                                                   │
│        • Test Accuracy: 90.40%                                              │
│        • Hit@1: 100% (top prediction = podium contender)                    │
│                                                                             │
│  🏁 race_finish_rf.joblib (Random Forest)                                   │
│     └─ Predicts race completion (non-DNF)                                   │
│        • Test Accuracy: 94.78%                                              │
│        • Hit@1: 100% (top prediction finishes)                              │
│                                                                             │
│  Metadata (JSON):                                                           │
│  └─ Feature list, training params, performance metrics                      │
│                                                                             │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │
                               ↓
           ╔═══════════════════════════════════════╗
           ║   PREDICTION GENERATION               ║
           ║   generate_fastf1_predictions.py      ║
           ║                                       ║
           ║  Input: gold_fastf1.race_prediction_  ║
           ║         features for 2024-2025       ║
           ╚═══════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│                        PREDICTIONS (Output)                                 │
│                                                                             │
│  ✓ gold_fastf1.race_predictions (938 records)                               │
│                                                                             │
│    Columns:                                                                 │
│    ├─ season, round, grand_prix_slug                                        │
│    ├─ driver_code, driver_name, team_name, grid_position                    │
│    ├─ win_probability (0.0 - 1.0)                                           │
│    ├─ podium_probability (0.0 - 1.0)                                        │
│    ├─ finish_probability (0.0 - 1.0)                                        │
│    └─ prediction_generated_at (timestamp)                                   │
│                                                                             │
│  ✓ gold_fastf1.race_win_predictions (470 records)                           │
│    └─ Top 10 winner predictions per race (winner_rank <= 10)                │
│                                                                             │
│  Coverage:                                                                  │
│  ├─ Races: 47 races (2024-2025)                                             │
│  ├─ Drivers: 20 drivers per race                                            │
│  └─ Total Predictions: 938                                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🔄 Data Processing Pipeline

### Stage 1: BRONZE → Raw Data Ingestion
```
Input:  Parquet files (2018-2025)
├─ bronze_fastf1/session_result/  (9,779 race records)
├─ bronze_fastf1/weather/         (31,776 weather obs)
└─ bronze_fastf1/laps/            (221,938 lap records)

Process:
├─ Read parquet with union_by_name (handles schema variations)
├─ Filter for season 2018-2025
├─ Create unified bronze tables in DuckDB

Output: 3 Bronze tables (263K+ total records)
└─ bronze_fastf1.session_result
   bronze_fastf1.weather
   bronze_fastf1.laps
```

### Stage 2: BRONZE → SILVER → Feature Aggregation
```
Input:  bronze_fastf1 tables

Process:
1. Aggregate weather by race
   - Average: air temp, track temp, humidity, wind, pressure
   - Maximum: rainfall
   - Flags: is_wet (rainfall > 0.5mm), is_humid (humidity > 70%)

2. Create career statistics
   - Aggregate across all races per driver
   - Calculate wins, podiums, average positions, percentages

3. Create venue-specific stats
   - Group by driver + venue (track)
   - Track performance history at each circuit

4. Create weather-condition stats
   - Classify races as wet/dry/humid
   - Calculate performance in each condition

5. Create team statistics
   - Aggregate team performance across all races
   - Team wins, podiums, average position

6. Create rolling form metrics
   - 5-race rolling window
   - Average finish, points, grid position

Output: 6 Silver tables (aggregated statistics)
├─ silver_fastf1.race_data (3,175 races + weather)
├─ silver_fastf1.driver_career_stats (43 drivers)
├─ silver_fastf1.driver_venue_stats (1,159 venue records)
├─ silver_fastf1.driver_weather_stats (condition-specific)
├─ silver_fastf1.team_stats (22 teams)
└─ silver_fastf1.driver_season_form (rolling metrics)
```

### Stage 3: SILVER → GOLD → Feature Engineering
```
Input:  silver_fastf1 tables

Process:
1. Join all silver tables
   - Match each race with career stats
   - Join venue history
   - Join weather conditions
   - Join season form
   - Join team stats

2. Create computed features
   - Win/podium percentages
   - Weather adaptation metrics
   - Grid deviation from venue avg
   - Normalized weather features

3. Generate targets
   - target_win: finish_position == 1
   - target_podium: finish_position <= 3
   - target_finish: dnf == 0

Output: 4 Gold tables (ML-ready)
├─ gold_fastf1.race_prediction_features
│  └─ 3,175 rows × 61 features (complete training set)
├─ gold_fastf1.win_prediction_dataset
│  └─ Curated for winner prediction
├─ gold_fastf1.podium_prediction_dataset
│  └─ Curated for podium prediction
└─ gold_fastf1.race_win_predictions
   └─ View with ranked predictions
```

### Stage 4: GOLD → Model Training
```
Input:  gold_fastf1.race_prediction_features (3,175 rows)

Data Split:
├─ Train:   2018-2022 (1,798 records, 90 wins, 270 podiums)
├─ Val:     2023 (439 records, 22 wins, 66 podiums)
├─ Test:    2024 (479 records, 24 wins, 72 podiums)
└─ Holdout: 2025 (459 records - for final evaluation)

Models Trained:
1. Winner Prediction
   ├─ Algorithm: Random Forest (500 trees)
   ├─ Hyperparams: max_depth=15, min_samples_split=10
   ├─ Features: 47 selected numeric features
   └─ Performance: Val AUC 0.9742 → Test AUC 0.9907

2. Podium Prediction
   ├─ Algorithm: Logistic Regression
   ├─ Preprocessing: StandardScaler
   ├─ Features: 47 features
   └─ Performance: Val AUC 0.9328 → Test AUC 0.9747

3. Finish Prediction
   ├─ Algorithm: Random Forest (500 trees)
   ├─ Features: 47 features
   └─ Performance: Test Accuracy 94.78%

Output: 3 trained models + metadata
├─ ml_artifacts/race_win_rf.joblib (.json)
├─ ml_artifacts/race_podium_logreg.joblib (.json)
└─ ml_artifacts/race_finish_rf.joblib (.json)
```

### Stage 5: Models → Predictions
```
Input:  
├─ gold_fastf1.race_prediction_features (2024-2025 data)
└─ Trained models from ml_artifacts/

Process:
1. Load models and feature specifications
2. Prepare features (NaN → 0, Inf → 0)
3. Generate probabilities
   - Winner: predict_proba → [0, 1]
   - Podium: predict_proba → [0, 1]
   - Finish: predict_proba → [0, 1]
4. Normalize if needed
5. Create prediction table with timestamps

Output: Predictions (938 records)
├─ gold_fastf1.race_predictions
│  └─ 938 rows: drivers × races × probability scores
├─ gold_fastf1.race_win_predictions
│  └─ View with top 10 ranked predictions per race
└─ Timestamped for versioning
```

## 🔀 Feature Flow Example

**Race: 2025 Australian GP, Driver: Lando Norris**

```
BRONZE INGESTION
├─ session_result: Grid 2, Finish ?, Points ?
└─ weather: Temp 22°C, Humidity 65%, No rain

SILVER AGGREGATION
├─ career_stats: 55 races, 5 wins, 15 podiums
├─ venue_stats: 3 races at Albert Park, 0 wins, 1 podium
├─ weather_stats: 
│  ├─ Dry: 45 races, 5 wins, avg finish 5.2
│  └─ Humid: 10 races, 0 wins, avg finish 7.1
├─ team_stats: McLaren - 10 wins, 35 podiums
└─ season_form: Last 5 races avg finish 3.2, 12 points

GOLD ENGINEERING (61 features)
├─ Career: career_wins=5, career_podiums=15, avg_finish=6.2
├─ Venue: races_at_venue=3, wins_at_venue=0, avg_finish_at_venue=6.5
├─ Weather: avg_air_temp=22, is_wet=0, normalized_humidity=0.65
├─ Form: points_last_5=12, avg_finish_last_5=3.2
├─ Team: team_wins=10, team_avg_finish=4.8
├─ Adaptation: dry_win_pct=0.11, wet_win_pct=0.00
└─ Computed: win_pct_at_venue=0.00, podium_pct_at_venue=0.33

ML PREDICTIONS
├─ Winner Model → win_probability: 0.28
├─ Podium Model → podium_probability: 0.68
└─ Finish Model → finish_probability: 0.95
```

## 📈 Feature Importance Hierarchy

```
Tier 1 - Highest Impact:
├─ Grid position (starting point)
├─ Career podiums/wins (proven ability)
└─ Venue-specific history (track fit)

Tier 2 - High Impact:
├─ Season form (momentum)
├─ Weather-specific performance (condition adaptation)
└─ Team capability (car quality)

Tier 3 - Supporting:
├─ Career averages (baseline)
├─ Weather conditions (race context)
├─ Normalized features (scaling)
└─ Team history (context)

Tier 4 - Contextual:
├─ Driver codes (identifiers)
├─ Timestamps (versioning)
└─ Other metadata
```

## 🎯 Accuracy Metrics by Task

```
Winner Prediction (AUC = 0.9907)
├─ Excellent discrimination (AUC > 0.9)
├─ Top prediction identifies winner 50% of time
├─ Top 3 predictions contain winner 100% of time
└─ Test accuracy: 94.78%

Podium Prediction (AUC = 0.9747)
├─ Excellent discrimination
├─ Top prediction is podium contender 100% of time
├─ Test accuracy: 90.40%
└─ Hit@3: 100%

Finish Prediction (Accuracy = 94.78%)
├─ High accuracy
├─ Identifies DNF risks reliably
└─ Useful for fantasy scoring
```

---

**Architecture Version**: 1.0  
**Data Coverage**: 2018-2025 (8 complete seasons)  
**Total Records Processed**: 263,000+  
**Production Status**: ✅ Operational
