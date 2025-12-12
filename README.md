# F1 Dash - Machine Learning Pipeline

![Status](https://img.shields.io/badge/Status-Production%20Ready-2E8B57?style=flat-square&logo=pinboard&logoColor=white)
![Seasons](https://img.shields.io/badge/Seasons-2018--2025-B22222?style=flat-square&logo=databricks&logoColor=white)
![Models](https://img.shields.io/badge/Models-3%20Trained-1E90FF?style=flat-square&logo=scikitlearn&logoColor=white)
![Warehouse](https://img.shields.io/badge/Warehouse-DuckDB-8A2BE2?style=flat-square&logo=duckdb&logoColor=white)
![Frontend](https://img.shields.io/badge/UI-Tailwind%20-%20React-0F172A?style=flat-square&logo=react&logoColor=61DAFB)

F1 Dash is a full-stack racing analytics platform that ingests 2018-2025 telemetry, weather, and session data, engineers 61 ML-ready features, trains three production models, and serves ranked race predictions to a frontend dashboard. This repository contains the entire data platform: ingestion scripts, DuckDB warehouse, model artifacts, APIs, documentation, and UI.

## Contents
1. Highlights and architecture
2. Pipeline stages and assets
3. Quick start and operational playbooks
4. Documentation map and data coverage
5. Feature inventory, API integration, directory guide
6. Troubleshooting and roadmap

---

## Highlights
- Columnar DuckDB warehouse with bronze, silver, and gold schemas plus cached FastF1 data
- Seasonal coverage across 3,198 session results, 31,776 weather points, and 221,938 laps
- Three reproducible models (winner, podium, finish) with best test AUC of 0.9907
- Automated runner `run_fastf1_ml_pipeline.py` orchestrates ingestion -> features -> training -> predictions
- Frontend (Tailwind + React) consumes `/api/races/*/predictions` endpoints to display leaderboards
- Documentation spans quick start, architecture, deep dives, and ML references for onboarding

---

## End-to-End Pipeline

### Architecture Overview
```
Parquet / FastF1 cache
        |
        v
Bronze (raw ingestion) -- scripts/build_bronze_fastf1_ml.py
        |
        v
Silver (aggregations, weather joins) -- scripts/build_silver_fastf1_ml.py
        |
        v
Gold (61 engineered features) -- scripts/build_gold_fastf1_ml.py
        |
        |--> Model training -- scripts/train_fastf1_models.py
        |--> Prediction export -- scripts/generate_fastf1_predictions.py
```

### Stage Summary
| Stage | Purpose | Output |
|-------|---------|--------|
| Bronze | Normalize raw FastF1 exports plus weather feeds | `bronze_fastf1.{session_result, laps, weather}` |
| Silver | Aggregate driver/team/venue stats and weather adaptation metrics | `silver_fastf1.{driver_venue_stats, driver_weather_stats, team_stats, driver_season_form}` |
| Gold | Assemble 61 ML-ready features per driver-race | `gold_fastf1.race_prediction_features` |
| Training | Fit winner RF, podium logistic regression, finisher RF | `ml_artifacts/*.joblib` with metadata |
| Prediction | Score 2024-2025 race grid and persist ranked outcomes | `gold_fastf1.race_predictions`, CSV exports |

---

## Key Assets

### Warehouse
- `warehouse/f1_openf1.duckdb` with bronze, silver, gold schemas and helper views
- `bronze_fastf1` surfaces session results, lap telemetry, and weather telemetry
- `silver_fastf1` enriches with venue history, rolling form, driver and team aggregates
- `gold_fastf1` stores prediction features plus the 938 generated forecasts

### ML Artifacts
- `ml_artifacts/race_win_rf.joblib` with JSON metadata summarizing 0.9907 test AUC
- `ml_artifacts/race_podium_logreg.joblib` covering podium classification
- `ml_artifacts/race_finish_rf.joblib` for finish probability

### Documentation
- `START_HERE.txt` and `QUICKSTART.md` for onboarding
- `F1_ML_PIPELINE_README.md` and `ARCHITECTURE.md` for deep technical dives
- `ML_PIPELINE_SUMMARY.md`, `ANALYSIS.md`, `PROJECT_COMPLETION_SUMMARY.txt` for executive-ready context

---

## Quick Start

### Requirements
- Python 3.13+, DuckDB 1.0+, pip, and 10 GB of free disk space
- Optional: Node 20+ for frontend work, Docker for container orchestration

### Environment Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # see package-lock if Node services are required
```

### Run the Full Pipeline
```bash
cd /Volumes/SAMSUNG/apps/f1-dash
python3 run_fastf1_ml_pipeline.py --all
```
Output: bronze ingestion -> silver aggregation -> gold feature engineering -> model training -> prediction export (~15 minutes on an M-series laptop).

### Execute Individual Stages
```bash
python3 scripts/build_bronze_fastf1_ml.py
python3 scripts/build_silver_fastf1_ml.py
python3 scripts/build_gold_fastf1_ml.py
python3 scripts/train_fastf1_models.py
python3 scripts/generate_fastf1_predictions.py
```

### Query Predictions
```sql
SELECT driver_name,
       team_name,
       ROUND(win_probability, 4) AS win_prob
FROM gold_fastf1.race_predictions
WHERE season = 2025
  AND grand_prix_slug = 'australian-grand-prix'
ORDER BY win_probability DESC
LIMIT 5;
```

---

## Documentation Map
| Topic | File | Focus |
|-------|------|-------|
| Orientation | `START_HERE.txt` | Repository layout, prerequisites |
| Quick execution | `QUICKSTART.md` | Fast pipeline execution steps |
| Architecture | `ARCHITECTURE.md` | Diagram-level explanation of flows |
| ML Deep Dive | `F1_ML_PIPELINE_README.md` | Algorithms, feature logic, troubleshooting |
| Operational summary | `ML_PIPELINE_SUMMARY.md` | Timing, KPIs, validation metrics |
| Opportunity log | `OPPORTUNITIES.md` | Future enhancements and experiments |

---

## Data Coverage

| Metric | Value |
|--------|-------|
| Seasons | 2018-2025 |
| Race sessions | 3,198 |
| Venues | 36 |
| Drivers | 43 |
| Teams | 22 |
| Weather records | 31,776 |
| Lap telemetry | 221,938 |
| Engineered features | 61 |
| Models trained | 3 |
| Stored predictions | 938 |

---

## Feature Engineering Inventory

- **Weather block (13 features):** air/track temperature, humidity, wind speed, pressure, rainfall intensity, categorical wet/dry/humid indicators
- **Career history (8 features):** lifetime wins, podiums, races, finish rate, win share, podium share, position gain
- **Venue proficiency (9 features):** venue wins/podiums, average grid, average finish, venue-specific win and podium percentages
- **Rolling form (3 features):** average finish, points, and grid position across the trailing five races
- **Team context (4 features):** team wins, podiums, points, and average finish for the current season
- **Weather adaptation (10 features):** dry/wet/humid counts and win ratios, finish deltas by condition
- **Computed indicators (5 features):** normalized weather, grid deltas, driver-team interaction metrics

---

## API and Frontend Integration
- Backend exposes `GET /api/races/{season}/{round}/predictions` and `GET /api/races/next/predictions`
- Responses leverage `gold_fastf1.race_predictions` joined with metadata from silver tables
- Frontend (React + Tailwind) renders a leaderboard, win probability sparkline, and contextual stats
- To refresh UI data, rerun the pipeline and restart backend services (`start_all.sh`)

---

## Directory Guide

| Path | Purpose |
|------|---------|
| `ingestion/`, `scripts/` | Source ingestion jobs, materialization scripts, orchestration helpers |
| `warehouse/`, `bronze*`, `fastf1_cache/` | Persistent DuckDB database and cached FastF1 exports |
| `ml_artifacts/`, `artifacts/` | Saved model binaries, JSON metadata, evaluation charts |
| `frontend/`, `api/`, `backend/` | UI client, API gateway, backend services |
| `docs` (root markdown files) | Architecture, runbooks, research notes, next steps |
| `docker/`, `docker-compose.yml` | Containerized deployment for ingestion + API stack |

---

## Troubleshooting & Support
- Review `F1_ML_PIPELINE_README.md` for validation SQL, schema definitions, and known issues
- Use `troubleshoot.py` to run automated health checks on DuckDB tables and model artifacts
- Inspect `batch_export_2025.log` and `weather_export_2025.log` for ingestion timing or throttling issues
- Regenerate caches with `run_fastf1_exports.py` if FastF1 telemetry becomes stale

---

## Status & Roadmap
- Version 2.0 finalized on Dec 7, 2025 with automated ML pipeline and refreshed documentation
- Open opportunities listed in `WHAT_TO_BUILD_NEXT.txt` and `OPPORTUNITIES.md`
- Future goals: extend to 2026 data, incorporate live timing streams, expose gRPC service for probabilities

For questions or onboarding, start with `START_HERE.txt`, then follow the quick start flow outlined above. This README is the canonical overview; all deeper references are linked throughout.
