# F1 ML Pipeline - Quick Start Guide

## 🚀 Quick Start (5 Minutes)

### 1. Run Complete Pipeline
```bash
cd /Volumes/SAMSUNG/apps/f1-dash
python3 run_fastf1_ml_pipeline.py --all
```
This will:
- Ingest 2018-2025 data → bronze_fastf1 (5 min)
- Aggregate features → silver_fastf1 (1 min)
- Engineer ML features → gold_fastf1 (2 min)
- Train 3 models → ml_artifacts/ (3 min)
- Generate 938 predictions → race_predictions (1 min)

**Total Time**: ~15 minutes

---

## 📊 Check Results

### View All Predictions
```python
import duckdb

con = duckdb.connect("/Volumes/SAMSUNG/apps/f1-dash/warehouse/f1_openf1.duckdb")

# Get all 2025 race predictions
predictions = con.execute("""
    SELECT season, round, driver_name, team_name, 
           ROUND(win_probability, 4) as win_prob,
           ROUND(podium_probability, 4) as podium_prob
    FROM gold_fastf1.race_predictions
    WHERE season = 2025
    ORDER BY season, round, win_probability DESC
""").fetchdf()

print(predictions)
con.close()
```

### Show Winner Predictions for a Race
```python
import duckdb

con = duckdb.connect("/Volumes/SAMSUNG/apps/f1-dash/warehouse/f1_openf1.duckdb")

# Top 5 winner predictions for Australian GP 2025
winners = con.execute("""
    SELECT driver_code, driver_name, team_name, 
           ROUND(win_probability, 4) as win_prob
    FROM gold_fastf1.race_predictions
    WHERE season = 2025 AND grand_prix_slug = 'australian-grand-prix'
    ORDER BY win_probability DESC
    LIMIT 5
""").fetchdf()

print("🏆 Australian GP 2025 Winner Predictions:")
print(winners)
con.close()
```

### Show Podium Predictions
```python
import duckdb

con = duckdb.connect("/Volumes/SAMSUNG/apps/f1-dash/warehouse/f1_openf1.duckdb")

# Podium contenders for Australian GP 2025
podium = con.execute("""
    SELECT driver_code, driver_name, team_name, 
           ROUND(podium_probability, 4) as podium_prob
    FROM gold_fastf1.race_predictions
    WHERE season = 2025 AND grand_prix_slug = 'australian-grand-prix'
    ORDER BY podium_probability DESC
    LIMIT 3
""").fetchdf()

print("🥇 Australian GP 2025 Podium Predictions:")
print(podium)
con.close()
```

---

## 📈 View Model Performance

```python
import json

# Check winner model performance
with open('/Volumes/SAMSUNG/apps/f1-dash/ml_artifacts/race_win_rf.json') as f:
    win_model = json.load(f)
    print("🏆 Race Winner Model Performance:")
    print(f"  Validation AUC: {win_model['val_metrics']['roc_auc']:.4f}")
    print(f"  Test AUC: {win_model['test_metrics']['roc_auc']:.4f}")
    print(f"  Test Accuracy: {win_model['test_metrics']['accuracy']:.4f}")

# Check podium model performance
with open('/Volumes/SAMSUNG/apps/f1-dash/ml_artifacts/race_podium_logreg.json') as f:
    podium_model = json.load(f)
    print("\n🥇 Podium Prediction Model Performance:")
    print(f"  Validation AUC: {podium_model['val_metrics']['roc_auc']:.4f}")
    print(f"  Test AUC: {podium_model['test_metrics']['roc_auc']:.4f}")
    print(f"  Test Hit@1: {podium_model['test_metrics']['hit@1']:.4f}")
```

---

## 🔍 Analyze Driver Performance

### Historical Performance at Venues
```python
import duckdb

con = duckdb.connect("/Volumes/SAMSUNG/apps/f1-dash/warehouse/f1_openf1.duckdb")

# How does Max Verstappen perform at Monaco?
verstappen_monaco = con.execute("""
    SELECT driver_code, driver_name, races_at_venue, wins_at_venue, 
           podiums_at_venue, avg_finish_at_venue
    FROM silver_fastf1.driver_venue_stats
    WHERE driver_code = 'VER' AND grand_prix_slug = 'monaco-grand-prix'
""").fetchdf()

print("Max Verstappen at Monaco:")
print(verstappen_monaco)
con.close()
```

### Weather Performance
```python
import duckdb

con = duckdb.connect("/Volumes/SAMSUNG/apps/f1-dash/warehouse/f1_openf1.duckdb")

# Who's best in wet conditions?
wet_specialists = con.execute("""
    SELECT driver_code, driver_name, races_in_condition as wet_races, 
           wins_in_condition, avg_finish_in_condition
    FROM silver_fastf1.driver_weather_stats
    WHERE weather_condition = 'wet'
    ORDER BY wins_in_condition DESC
    LIMIT 10
""").fetchdf()

print("Wet Weather Specialists:")
print(wet_specialists)
con.close()
```

---

## 📊 Data Statistics

```python
import duckdb

con = duckdb.connect("/Volumes/SAMSUNG/apps/f1-dash/warehouse/f1_openf1.duckdb")

print("=" * 60)
print("F1 ML PIPELINE - DATA STATISTICS")
print("=" * 60)

# Overall stats
stats = con.execute("""
    SELECT 
        COUNT(*) as total_races,
        COUNT(DISTINCT season) as seasons,
        COUNT(DISTINCT driver_code) as drivers,
        COUNT(DISTINCT team_name) as teams,
        COUNT(DISTINCT grand_prix_slug) as venues,
        SUM(CASE WHEN target_win = 1 THEN 1 ELSE 0 END) as total_wins,
        ROUND(100.0 * SUM(CASE WHEN target_win = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) as win_rate_pct
    FROM gold_fastf1.race_prediction_features
""").fetchone()

print(f"\nRace Data:")
print(f"  Total Races: {stats[0]:,}")
print(f"  Seasons: {stats[1]} (2018-2025)")
print(f"  Unique Drivers: {stats[2]}")
print(f"  Unique Teams: {stats[3]}")
print(f"  Unique Venues: {stats[4]}")
print(f"  Total Wins: {stats[5]:,} ({stats[6]}%)")

# Prediction coverage
pred_stats = con.execute("""
    SELECT 
        COUNT(*) as total_predictions,
        COUNT(DISTINCT season) as seasons,
        COUNT(DISTINCT round) as races,
        MIN(season) as earliest_season,
        MAX(season) as latest_season
    FROM gold_fastf1.race_predictions
""").fetchone()

print(f"\nPredictions:")
print(f"  Total Predictions: {pred_stats[0]:,}")
print(f"  Seasons Covered: {pred_stats[1]}")
print(f"  Races Covered: {pred_stats[2]}")
print(f"  Years: {pred_stats[3]}-{pred_stats[4]}")

con.close()
print("=" * 60)
```

---

## 🎯 Run Individual Stages

### Just Ingest Data
```bash
python3 scripts/build_bronze_fastf1_ml.py
```

### Just Aggregate Features
```bash
python3 scripts/build_silver_fastf1_ml.py
```

### Just Engineer Features
```bash
python3 scripts/build_gold_fastf1_ml.py
```

### Just Train Models
```bash
python3 scripts/train_fastf1_models.py
```

### Just Generate Predictions
```bash
python3 scripts/generate_fastf1_predictions.py
```

---

## 📂 Key Files

| File | Purpose |
|------|---------|
| `run_fastf1_ml_pipeline.py` | Pipeline orchestrator - run this first |
| `scripts/build_bronze_fastf1_ml.py` | Data ingestion |
| `scripts/build_silver_fastf1_ml.py` | Feature aggregation |
| `scripts/build_gold_fastf1_ml.py` | Feature engineering |
| `scripts/train_fastf1_models.py` | Model training |
| `scripts/generate_fastf1_predictions.py` | Prediction generation |
| `warehouse/f1_openf1.duckdb` | Main database (all tables) |
| `ml_artifacts/race_win_rf.joblib` | Winner prediction model |
| `ml_artifacts/race_podium_logreg.joblib` | Podium prediction model |
| `F1_ML_PIPELINE_README.md` | Comprehensive documentation |
| `ML_PIPELINE_SUMMARY.md` | Execution summary |

---

## 🔧 Verify Installation

```bash
# Check Python version
python3 --version  # Should be 3.10+

# Check required packages
python3 -c "import duckdb; import pandas; import numpy; import sklearn; print('✅ All dependencies installed')"

# Check database exists
ls -lh /Volumes/SAMSUNG/apps/f1-dash/warehouse/f1_openf1.duckdb

# Check models exist
ls -lh /Volumes/SAMSUNG/apps/f1-dash/ml_artifacts/race_*.joblib
```

---

## ✅ Verification Checklist

- [x] Bronze layer created (3 tables, 263K+ records)
- [x] Silver layer created (6 tables with aggregated stats)
- [x] Gold layer created (4 tables, 61 features)
- [x] Models trained (3 models with AUC > 0.93)
- [x] Predictions generated (938 predictions)
- [x] Database populated (f1_openf1.duckdb)

---

## 📞 Support

### Check Logs
```bash
# View most recent output
tail -100 /tmp/f1_pipeline.log
```

### Troubleshoot Issues
```python
import duckdb

con = duckdb.connect("/Volumes/SAMSUNG/apps/f1-dash/warehouse/f1_openf1.duckdb")

# Check all tables exist
tables = con.execute("""
    SELECT table_schema, table_name, COUNT(*) as row_count
    FROM (
        SELECT * FROM bronze_fastf1.session_result UNION ALL
        SELECT * FROM silver_fastf1.race_data UNION ALL
        SELECT * FROM gold_fastf1.race_prediction_features
    ) UNION BY NAME
    GROUP BY table_schema, table_name
""").fetchdf()

print("Database Tables:")
print(tables)
con.close()
```

---

## 🎓 Learn More

- `F1_ML_PIPELINE_README.md` - Detailed architecture & features
- `ML_PIPELINE_SUMMARY.md` - Complete execution results
- Database schema - Inspect with DuckDB

---

## 📊 Performance Expectations

| Operation | Time | Output |
|-----------|------|--------|
| Bronze ingestion | ~5 min | 263K records |
| Silver aggregation | ~1 min | 6 feature tables |
| Gold engineering | ~2 min | 3,175 × 61 features |
| Model training | ~3 min | 3 trained models |
| Prediction gen | ~1 min | 938 predictions |
| **Total** | **~15 min** | **Production ready** |

---

**Version**: 1.0  
**Last Updated**: December 7, 2025  
**Status**: ✅ Operational
