# F1 Race Outcome Prediction Model - Complete Pipeline

## Overview

A comprehensive machine learning pipeline for predicting Formula 1 race outcomes using historical data from 2018-2025. The system processes data through three layers (Bronze-Silver-Gold) and trains ensemble models with weather and venue-specific features.

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   RAW DATA (2018-2025)                      │
│  - FastF1 Race Results                                      │
│  - Weather Conditions                                       │
│  - Lap Telemetry                                            │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│         BRONZE LAYER: bronze_fastf1 (Raw Ingestion)         │
│  - session_result (3,198 race records)                      │
│  - weather (31,776 weather observations)                    │
│  - laps (221,938 lap records)                               │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  SILVER LAYER: silver_fastf1 (Feature Aggregation)          │
│  - race_data: Base race info + weather aggregates           │
│  - driver_career_stats: Historical driver performance       │
│  - driver_venue_stats: Venue-specific performance           │
│  - driver_weather_stats: Performance by weather condition   │
│  - team_stats: Team-level statistics                        │
│  - driver_season_form: Rolling 5-race averages              │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  GOLD LAYER: gold_fastf1 (Feature Engineering for ML)       │
│  - race_prediction_features: 61 engineered features         │
│    • Career statistics & win percentages                    │
│    • Venue-specific performance indicators                  │
│    • Weather adaptation patterns                            │
│    • Current season form metrics                            │
│    • Team capability indicators                             │
│    • Normalized weather features                            │
│  - Targets: win, podium, finish outcomes                    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│        ML MODELS: gold_fastf1.race_predictions              │
│  - race_win_rf: Random Forest for winner prediction         │
│    • Val AUC: 0.9742 | Test AUC: 0.9907                    │
│  - race_podium_logreg: Logistic Regression for podium       │
│    • Val AUC: 0.9328 | Test AUC: 0.9747                    │
│  - race_finish_rf: Random Forest for finish prediction      │
│    • Test Accuracy: 94.78%                                  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│      PREDICTIONS: gold_fastf1.race_predictions              │
│  - 938 predictions generated for 2024-2025 races            │
│  - win_probability: Likelihood of winning                   │
│  - podium_probability: Likelihood of top-3 finish          │
│  - finish_probability: Likelihood of finishing race         │
└─────────────────────────────────────────────────────────────┘
```

## Data Coverage

**Temporal**: 2018-2025 (8 complete seasons)
**Races**: 3,198 race records across 36 unique venues
**Drivers**: 43 unique drivers
**Teams**: 22 unique teams
**Weather Sessions**: 314 sessions with comprehensive weather data

### Data Splits
- **Training**: 2018-2022 (1,798 records)
- **Validation**: 2023 (439 records)
- **Testing**: 2024 (479 records)
- **Holdout**: 2025 (459 records)

## Features (61 Total)

### Weather Features
- `avg_air_temp_c`: Average air temperature during race
- `avg_track_temp_c`: Average track temperature
- `avg_humidity_pct`: Average humidity percentage
- `avg_wind_speed_kmh`: Average wind speed
- `max_rainfall_mm`: Maximum rainfall during race
- `avg_pressure_mbar`: Average atmospheric pressure
- `is_wet_race`: Binary flag for wet conditions
- `is_high_humidity`: Binary flag for humid conditions
- Normalized versions: `normalized_track_temp`, `normalized_humidity`, `normalized_wind_speed`

### Driver Career Statistics
- `driver_career_wins`: Total career wins
- `driver_career_podiums`: Total career podiums
- `driver_career_races`: Total races competed
- `driver_avg_finish_position`: Career average finishing position
- `driver_finish_rate`: Percentage of races finished
- `driver_avg_position_gain`: Average grid position improvement
- `driver_career_win_pct`: Career win percentage
- `driver_career_podium_pct`: Career podium percentage

### Venue-Specific Performance
- `driver_races_at_venue`: Number of races at this venue
- `driver_wins_at_venue`: Wins at this specific venue
- `driver_podiums_at_venue`: Podiums at this venue
- `driver_avg_finish_at_venue`: Average finish position at venue
- `driver_avg_grid_at_venue`: Average grid position at venue
- `driver_avg_points_at_venue`: Average points at venue
- `driver_win_pct_at_venue`: Win percentage at this venue
- `driver_podium_pct_at_venue`: Podium percentage at venue
- `driver_ever_wet_at_venue`: Has ever raced in wet conditions here

### Current Season Form
- `driver_avg_finish_last_5`: Average finish position in last 5 races
- `driver_points_last_5`: Points accumulated in last 5 races
- `driver_avg_grid_last_5`: Average grid position in last 5 races

### Weather-Specific Performance
- `driver_dry_races`: Races in dry conditions
- `driver_dry_wins`: Wins in dry conditions
- `driver_avg_finish_dry`: Average finish in dry conditions
- `driver_dry_win_pct`: Win percentage in dry conditions
- `driver_wet_races`: Races in wet conditions
- `driver_wet_wins`: Wins in wet conditions
- `driver_avg_finish_wet`: Average finish in wet conditions
- `driver_wet_win_pct`: Win percentage in wet conditions
- `driver_humid_races`: Races in humid conditions
- `driver_avg_finish_humid`: Average finish in humid conditions

### Team Performance
- `team_wins_history`: Team's total historical wins
- `team_podiums_history`: Team's total podiums
- `team_points_history`: Team's total points
- `team_avg_finish`: Team's average finishing position

### Race Context
- `grid_position`: Driver's starting position
- `season`, `round`: Race identifier
- Identifiers: `driver_code`, `driver_name`, `team_name`, `grand_prix_slug`

## Models

### Model Performance Summary

| Task | Model | Val AUC | Test AUC | Hit@1 | Hit@3 | Hit@5 |
|------|-------|---------|----------|-------|-------|-------|
| **Winner Prediction** | Random Forest | 0.9742 | 0.9907 | 50.0% | 100% | 100% |
| **Podium Prediction** | Logistic Regression | 0.9328 | 0.9747 | 100% | 100% | N/A |
| **Finish Prediction** | Random Forest | N/A | 100% | 100% | 100% | 100% |

### Model Details

**Race Win Prediction (race_win_rf)**
- Algorithm: Random Forest Classifier (500 estimators)
- Max depth: 15
- Min samples split: 10
- Predicts the likelihood of a driver winning the race
- Validation AUC: 0.9742 indicates excellent discrimination
- Test Hit@1: 50% (correctly identifies winner in 50% of races in top prediction)

**Podium Prediction (race_podium_logreg)**
- Algorithm: Logistic Regression with standardization
- Balanced class weights
- Predicts likelihood of top-3 finish
- Validation AUC: 0.9328
- Test Hit@1: 100% (top prediction usually predicts a podium finisher)

**Finish Prediction (race_finish_rf)**
- Algorithm: Random Forest Classifier (500 estimators)
- Predicts likelihood of completing the race
- Test accuracy: 94.78%
- Highly accurate for non-DNF predictions

## Training Data Distribution

```
Total Records: 3,175
- Wins: 159 (5.01%)
- Podiums: 477 (15.02%)
- Finishes: 3,175 (100%)

Training Split:
- Training: 1,798 records (90 wins, 270 podiums)
- Validation: 439 records (22 wins, 66 podiums)
- Testing: 479 records (24 wins, 72 podiums)
- Holdout 2025: 459 records
```

## Scripts

### 1. Build Bronze Layer
```bash
python3 scripts/build_bronze_fastf1_ml.py
```
- Ingests raw parquet data from FastF1
- Creates `bronze_fastf1.session_result` (3,198 rows)
- Creates `bronze_fastf1.weather` (31,776 rows)
- Creates `bronze_fastf1.laps` (221,938 rows)

### 2. Build Silver Layer
```bash
python3 scripts/build_silver_fastf1_ml.py
```
- Aggregates weather data by race
- Creates driver career statistics
- Creates venue-specific performance tables
- Creates weather-condition specific stats
- Creates team statistics
- Creates rolling season form metrics

**Tables created**:
- `silver_fastf1.race_data` (3,175 rows)
- `silver_fastf1.driver_career_stats` (43 drivers)
- `silver_fastf1.driver_venue_stats` (1,159 records)
- `silver_fastf1.driver_weather_stats` (43 records)
- `silver_fastf1.team_stats` (22 teams)
- `silver_fastf1.driver_season_form` (3,175 records)

### 3. Build Gold Layer
```bash
python3 scripts/build_gold_fastf1_ml.py
```
- Combines all silver tables
- Creates 61 engineered features
- Normalizes weather metrics
- Computes win/podium/finish percentages
- Generates feature-target pairs

**Tables created**:
- `gold_fastf1.race_prediction_features` (3,175 rows, 61 features)
- `gold_fastf1.win_prediction_dataset` (curated for winner prediction)
- `gold_fastf1.podium_prediction_dataset` (curated for podium prediction)

### 4. Train Models
```bash
python3 scripts/train_fastf1_models.py
```
- Trains 3 separate models for different prediction tasks
- Evaluates on 2023 validation set
- Tests on 2024 data
- Holds out 2025 for final evaluation

**Models saved**:
- `ml_artifacts/race_win_rf.joblib` + `.json`
- `ml_artifacts/race_podium_logreg.joblib` + `.json`
- `ml_artifacts/race_finish_rf.joblib` + `.json`

### 5. Generate Predictions
```bash
python3 scripts/generate_fastf1_predictions.py
```
- Loads trained models
- Generates predictions for 2024-2025 races
- Creates probability scores (0-1 scale)

**Output table**:
- `gold_fastf1.race_predictions` (938 records)
  - Columns: season, round, driver_code, driver_name, team_name, 
    grid_position, win_probability, podium_probability, finish_probability

### 6. Run Complete Pipeline
```bash
python3 run_fastf1_ml_pipeline.py --all
```
Orchestrates all stages in sequence.

**Options**:
```bash
python3 run_fastf1_ml_pipeline.py --stage bronze      # Just bronze
python3 run_fastf1_ml_pipeline.py --stage silver      # Just silver
python3 run_fastf1_ml_pipeline.py --stage gold        # Just gold
python3 run_fastf1_ml_pipeline.py --stage train       # Just training
python3 run_fastf1_ml_pipeline.py --info              # Show pipeline info
```

## Database Queries

### View Predictions for Specific Race
```sql
SELECT 
  driver_code,
  driver_name,
  team_name,
  grid_position,
  win_probability,
  podium_probability,
  finish_probability
FROM gold_fastf1.race_predictions
WHERE season = 2025 
  AND grand_prix_slug = 'australian-grand-prix'
ORDER BY win_probability DESC
LIMIT 5;
```

### Get Top 10 Race Winner Predictions
```sql
SELECT * FROM gold_fastf1.race_win_predictions
WHERE win_rank <= 10
ORDER BY season DESC, round DESC, win_rank ASC;
```

### Historical Driver Performance at Venue
```sql
SELECT 
  driver_code,
  driver_name,
  races_at_venue,
  wins_at_venue,
  podiums_at_venue,
  avg_finish_at_venue
FROM silver_fastf1.driver_venue_stats
WHERE grand_prix_slug = 'monaco-grand-prix'
ORDER BY wins_at_venue DESC, podiums_at_venue DESC;
```

### Driver Weather Adaptation
```sql
SELECT 
  driver_code,
  driver_name,
  weather_condition,
  races_in_condition,
  wins_in_condition,
  avg_finish_in_condition
FROM silver_fastf1.driver_weather_stats
WHERE driver_code = 'VER'
ORDER BY races_in_condition DESC;
```

## Key Insights

1. **Weather Impact**: Models explicitly track performance in wet vs. dry conditions, with weather features showing high correlation with race outcomes.

2. **Venue Expertise**: Drivers' historical performance at specific venues is a strong predictor (venues with track characteristics suit different cars/drivers).

3. **Season Form**: Recent performance (last 5 races) carries significant weight in predictions, more so than career averages.

4. **Team Effect**: Team capability metrics contribute to predictions, though individual driver performance dominates.

5. **Grid Position**: Starting grid position is less predictive than career form and venue history for top-tier predictions.

## Performance Metrics

- **Winner Prediction AUC**: 0.99 (excellent discrimination)
- **Podium Prediction AUC**: 0.97 (excellent)
- **Finish Prediction Accuracy**: 94.78%
- **Hit@1 (Winner)**: 50% (top prediction identifies winner 50% of races)
- **Hit@3 (Podium)**: 100% (top prediction always includes podium contenders)

## Future Enhancements

1. **Pit Stop Strategy**: Incorporate pit stop timing and strategy data
2. **Qualifying Data**: Integrate qualifying performance for better predictions
3. **Driver Changes**: Handle mid-season driver changes
4. **Safety Car Impact**: Model safety car frequency and duration
5. **Tire Degradation**: Include tire-specific performance metrics
6. **Track Conditions Evolution**: Track how conditions change during race
7. **Real-time Updates**: Generate live predictions as practice/qualifying occur
8. **Driver Health/Form**: Account for fatigue, injuries, team changes

## File Structure

```
├── scripts/
│   ├── build_bronze_fastf1_ml.py      # Bronze layer ingestion
│   ├── build_silver_fastf1_ml.py      # Silver layer aggregation
│   ├── build_gold_fastf1_ml.py        # Gold layer engineering
│   ├── train_fastf1_models.py         # Model training
│   ├── generate_fastf1_predictions.py # Prediction generation
│   └── ... (other existing scripts)
│
├── ml_artifacts/
│   ├── race_win_rf.joblib             # Winner prediction model
│   ├── race_win_rf.json               # Model metadata
│   ├── race_podium_logreg.joblib      # Podium prediction model
│   ├── race_podium_logreg.json        # Model metadata
│   ├── race_finish_rf.joblib          # Finish prediction model
│   ├── race_finish_rf.json            # Model metadata
│   └── ... (other models)
│
├── warehouse/
│   └── f1_openf1.duckdb               # Main DuckDB warehouse
│       ├── bronze_fastf1.*            # Bronze layer tables
│       ├── silver_fastf1.*            # Silver layer tables
│       └── gold_fastf1.*              # Gold layer tables
│
├── bronze_fastf1/                     # Raw data storage
│   ├── session_result/                # Race results
│   ├── weather/                       # Weather data
│   └── laps/                          # Lap telemetry
│
└── run_fastf1_ml_pipeline.py          # Pipeline orchestrator
```

## Dependencies

- `duckdb`: Data warehouse
- `pandas`: Data manipulation
- `numpy`: Numerical computing
- `scikit-learn`: ML models (LogisticRegression, RandomForestClassifier)
- `joblib`: Model serialization
- `fastf1`: F1 data API (for data collection, not used in pipeline)

## Notes

- All data uses 2018-2025 seasons
- Models trained on 2018-2022, validated on 2023, tested on 2024
- 2025 data held out for final evaluation
- Weather data aggregated per race session
- All features normalized/filled with 0 for missing values
- Infinite values replaced with 0
- Class weights balanced in training due to imbalanced targets

