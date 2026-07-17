import numpy as np
import pickle
import os
import matplotlib.pyplot as plt
from config import PROCESSED_DATA_DIR, RESULTS_DIR
# ============================================================
# PARAMETERS
# ============================================================
C = 10
D = 10
A0 = 0.2
SEEDS = 4

base_path = PROCESSED_DATA_DIR / f"C0-{C},D-{D}" / f"C0-{C},D-{D},A0-{A0}"

all_ar_trajectories = []

print(f"Calculating Aspect Ratio Trajectories across {SEEDS} seeds...")

for i in range(1, SEEDS + 1):
    filepath = base_path / f"SEED{i}" / "datas.pkl"
print(f"  Processing Seed {i}...")

    if not filepath.exists():
        print(f"    File not found: {filepath}")
        continue
    
    with open(filepath, "rb") as f:
        data = pickle.load(f)
        
    data = data[:-1]
    seed_ar = []
    
    # Loop through every time frame in the simulation
    for frame_data in data:
        frame = np.array(frame_data)
        
        idx_col = frame[:, 1]
        lf_col = frame[:, 10]
        df_col = frame[:, 11]
        live_col = frame[:, 15]
        
        # Filter for ONLY ALIVE (1) and SENSITIVE (idx == 1)
        mask = (live_col == 1) & (idx_col == 1)
        
        lf_sens = lf_col[mask]
        df_sens = df_col[mask]
        
        # Calculate aspect ratio (Length / Diameter)
        if len(lf_sens) > 0:
            aspect_ratios = lf_sens / df_sens
            seed_ar.append(np.mean(aspect_ratios))
        else:
            # If they die out, append NaN so it doesn't skew the mean
            seed_ar.append(np.nan) 
            
    all_ar_trajectories.append(seed_ar)

# ============================================================
# CALCULATE MEAN AND VARIANCE & PLOT
# ============================================================
if all_ar_trajectories:
    min_len = min(len(traj) for traj in all_ar_trajectories)
    trimmed_trajectories = np.array([traj[:min_len] for traj in all_ar_trajectories])
    
    # Use nanmean and nanstd to safely ignore frames where the strain went extinct
    mean_ar = np.nanmean(trimmed_trajectories, axis=0)
    std_ar = np.nanstd(trimmed_trajectories, axis=0)
    time_steps = np.arange(min_len)

    plt.figure(figsize=(8, 5))
    
    plt.fill_between(time_steps, mean_ar - std_ar, mean_ar + std_ar, color='#FF495C', alpha=0.2)
    plt.plot(time_steps, mean_ar, color='#FF495C', linewidth=3, label='Mean Aspect Ratio (Sensitive)')

    # Add a horizontal line marking the un-elongated baseline (3.0)
    plt.axhline(3.0, color='black', linestyle='--', linewidth=1.5, alpha=0.7, label='Normal Cell Baseline')

    plt.title(f"Mean Aspect Ratio Over Time ($C_0={C}, D={D}, A_0={A0}$)")
    plt.xlabel("Simulation Frames")
    plt.ylabel("Aspect Ratio ($L / d$)")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()

    plot_filename = RESULTS_DIR / "Aspect_Ratio_Trajectory.png"
    plt.savefig(plot_filename, dpi=300)
    print(f"\nSuccess! Saved trajectory to {plot_filename}")
else:
    print("No data was loaded.")