#!/usr/bin/env python3
"""
Master pipeline script for F1 race outcome prediction.

Orchestrates the entire ETL and ML pipeline:
1. Build bronze_fastf1 - Raw data ingestion (2018-2025)
2. Build silver_fastf1 - Feature aggregation with weather
3. Build gold_fastf1 - Feature engineering for ML
4. Train models - Build prediction models
5. Generate predictions - Create race outcome predictions

Usage:
    python run_fastf1_ml_pipeline.py [--stage stage_name] [--debug]
    
    Stages:
    - bronze: Build bronze layer only
    - silver: Build silver layer (requires bronze)
    - gold: Build gold layer (requires silver)
    - train: Train models (requires gold)
    - predict: Generate predictions (requires trained models)
    - all: Run complete pipeline (default)
"""

import argparse
import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("fastf1_ml_pipeline")

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"

PIPELINE_STAGES = {
    "bronze": {
        "script": "build_bronze_fastf1_ml.py",
        "description": "Ingest raw race and weather data (2018-2025)",
        "depends_on": []
    },
    "silver": {
        "script": "build_silver_fastf1_ml.py",
        "description": "Create aggregated features with weather & venue stats",
        "depends_on": ["bronze"]
    },
    "gold": {
        "script": "build_gold_fastf1_ml.py",
        "description": "Build comprehensive feature-engineered training dataset",
        "depends_on": ["silver"]
    },
    "train": {
        "script": "train_fastf1_models.py",
        "description": "Train prediction models on gold dataset",
        "depends_on": ["gold"]
    },
}


def run_stage(stage: str, debug: bool = False) -> bool:
    """Run a single pipeline stage."""
    if stage not in PIPELINE_STAGES:
        logger.error(f"Unknown stage: {stage}")
        return False
    
    config = PIPELINE_STAGES[stage]
    script_path = SCRIPTS_DIR / config["script"]
    
    if not script_path.exists():
        logger.error(f"Script not found: {script_path}")
        return False
    
    logger.info(f"\n{'='*70}")
    logger.info(f"Stage: {stage.upper()}")
    logger.info(f"Description: {config['description']}")
    logger.info(f"Script: {script_path}")
    logger.info(f"{'='*70}\n")
    
    try:
        cmd = [sys.executable, str(script_path)]
        result = subprocess.run(cmd, check=True, capture_output=False)
        logger.info(f"✓ Stage '{stage}' completed successfully\n")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"✗ Stage '{stage}' failed with exit code {e.returncode}")
        return False
    except Exception as e:
        logger.error(f"✗ Stage '{stage}' failed: {e}")
        return False


def run_pipeline(stages: List[str], debug: bool = False) -> bool:
    """Run multiple pipeline stages in sequence."""
    logger.info(f"Starting F1 ML Pipeline with stages: {', '.join(stages)}")
    logger.info(f"Debug mode: {debug}\n")
    
    completed = []
    failed = []
    
    for stage in stages:
        logger.info(f"[{len(completed)+1}/{len(stages)}] Running stage: {stage}")
        
        if run_stage(stage, debug):
            completed.append(stage)
        else:
            failed.append(stage)
            logger.warning(f"Stopping pipeline due to failure in stage: {stage}")
            break
    
    # Summary
    logger.info(f"\n{'='*70}")
    logger.info("PIPELINE SUMMARY")
    logger.info(f"{'='*70}")
    logger.info(f"Completed: {len(completed)}/{len(stages)}")
    if completed:
        logger.info(f"  ✓ {', '.join(completed)}")
    if failed:
        logger.info(f"Failed: {len(failed)}")
        logger.info(f"  ✗ {', '.join(failed)}")
    logger.info(f"{'='*70}\n")
    
    return len(failed) == 0


def show_pipeline_info():
    """Display pipeline information."""
    print("\nF1 Race Prediction Model Pipeline")
    print("=" * 70)
    print("\nPipeline Stages:\n")
    
    for i, (stage_name, config) in enumerate(PIPELINE_STAGES.items(), 1):
        print(f"{i}. {stage_name.upper():8s} - {config['description']}")
        if config['depends_on']:
            print(f"   Requires: {', '.join(config['depends_on'])}")
    
    print("\n" + "=" * 70)
    print("\nUsage Examples:")
    print("  python run_fastf1_ml_pipeline.py --all              # Run complete pipeline")
    print("  python run_fastf1_ml_pipeline.py --stage bronze     # Run bronze stage only")
    print("  python run_fastf1_ml_pipeline.py --stage silver     # Run silver stage (requires bronze)")
    print("  python run_fastf1_ml_pipeline.py --debug            # Run with debug logging")
    print("\n" + "=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="F1 race prediction ML pipeline orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_fastf1_ml_pipeline.py --all           Run complete pipeline
  python run_fastf1_ml_pipeline.py --stage bronze  Run bronze stage only
  python run_fastf1_ml_pipeline.py --stage train   Run training stage (requires prior stages)
        """
    )
    
    parser.add_argument(
        "--stage",
        choices=list(PIPELINE_STAGES.keys()),
        help="Run specific pipeline stage"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all pipeline stages"
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show pipeline information"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    if args.info:
        show_pipeline_info()
        return 0
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Determine stages to run
    if args.all:
        stages_to_run = list(PIPELINE_STAGES.keys())
    elif args.stage:
        stages_to_run = [args.stage]
    else:
        show_pipeline_info()
        return 1
    
    # Run pipeline
    success = run_pipeline(stages_to_run, args.debug)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
