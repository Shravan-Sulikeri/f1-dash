#!/bin/bash
# F1 LakeHouse - Convenience script runner
# Automatically uses the project virtual environment

VENV_PYTHON="/Volumes/SAMSUNG/apps/f1-dash/.venv/bin/python"
PROJECT_DIR="/Volumes/SAMSUNG/apps/f1-dash"

# Change to project directory
cd "$PROJECT_DIR" || exit 1

# Run the requested script with all arguments
exec "$VENV_PYTHON" "$@"
