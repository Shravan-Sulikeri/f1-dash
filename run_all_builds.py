
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
SCRIPTS_DIR = REPO_ROOT / "scripts"

def run_script(script_name):
    script_path = SCRIPTS_DIR / script_name
    print(f"Running {script_name}...")
    subprocess.run([sys.executable, str(script_path)])

def main():
    run_script("build_silver.py")
    run_script("build_gold.py")
    run_script("build_ml_features.py")
    run_script("train_models.py")
    run_script("generate_race_predictions.py")

if __name__ == "__main__":
    main()
