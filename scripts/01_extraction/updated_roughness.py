import numpy as np
import pickle
import os
from config import RAW_DATA_DIR, PROCESSED_DATA_DIR
# ============================================================
# PARAMETERS
# ============================================================
SEEDS = list(range(1, 17))
Roughness = []

Lx, Ly = 200, 400
dx = 1
x_iterations = int(Lx / dx)

# Define your base directory path here
# Replaced hardcoded base_path with pathlib
C, D = 100, 10
base_path = RAW_DATA_DIR / f"C0-{C},D-{D}"

for i in SEEDS:
    filepath = base_path / f"SEED{i}" / "datas.pkl"
    print(f"Processing Roughness for Seed {i}...")
    
    if not filepath.exists():
        print(f"  File not found: {filepath}")
        Roughness.append(0.0)
        continue

    # Load the binary data
    with open(filepath, "rb") as f:
        data = pickle.load(f)
    
    # Remove the bounding box data at the end and grab the last frame
    data = data[:-1]
    frame = np.array(data[-1])
    
    # Extract columns based on collect_data.py indexing
    x_col = frame[:, 2]
    y_col = frame[:, 3]
    live_col = frame[:, 15]

    # Filter for ALIVE cells to trace the true active edge
    mask = (live_col == 1)
    x_live = x_col[mask]
    y_live = y_col[mask]

    Y_max = []

    # Slice the colony into vertical bins and find the highest Y in each bin
    for x_n in range(x_iterations):
        # Find cells falling within this vertical x-slice
        in_slice = (x_live >= x_n * dx) & (x_live < (x_n + 1) * dx)
        y_in_slice = y_live[in_slice]
        
        if len(y_in_slice) > 0:                      
            Y_max.append(np.max(y_in_slice))

    # Calculate standard deviation of the edge heights (Roughness)
    if len(Y_max) > 0:
        R = np.std(Y_max)
        Roughness.append(R)
    else:
        Roughness.append(0.0)

np.savetxt(PROCESSED_DATA_DIR / "Roughness.txt", np.array([SEEDS, Roughness]).T, delimiter="   ", header="Seed   Roughness")
print("Roughness analysis complete. Saved to Roughness.txt")