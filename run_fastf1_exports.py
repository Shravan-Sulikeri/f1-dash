
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "fastf1_export_season.py"

def main():
    for year in range(2018, 2025):
        print(f"Running export for year {year}...")
        subprocess.run([sys.executable, str(SCRIPT_PATH), "--year", str(year), "--auto-format", "--include-testing"])

if __name__ == "__main__":
    main()
