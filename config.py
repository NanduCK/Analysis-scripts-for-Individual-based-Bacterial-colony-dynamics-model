# scripts/config.py
from pathlib import Path

# Base paths (relative to the repository root)
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
RESULTS_DIR = BASE_DIR / "results"

# Environment mapping
CD_to_delta = {
    (10, 10): 0.0611,     
    (50, 50): 0.236,     
    (100, 100): 0.533,   
    (150, 150): 0.866,   
    (200, 200): 1.19,   
    (300, 100): 1.09,   
    (300, 250): 1.29    
}