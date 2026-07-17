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
all_fitness_trajectories = []

print(f"Calculating Fitness Trajectories across {SEEDS} seeds...")

for i in range(1, SEEDS + 1):
    filepath = base_path / f"SEED{i}" / "datas.pkl"
    print(f"  Processing Seed {i}...")

    if not filepath.exists():
        print(f"    File not found: {filepath}")
        continue
    
    with open(filepath, "rb") as f:
        data = pickle.load(f)
        
    # Drop the bounding box data at the end
    data = data[:-1]
    
    seed_fitness = []
    
    # Loop through every time frame in the simulation
    for frame_data in data:
        frame = np.array(frame_data)
        
        idx_col = frame[:, 1]
        live_col = frame[:, 15]
        
        # Count living Sensitive (1) and Resistant (0) cells
        sens_count = np.sum((live_col == 1) & (idx_col == 1))
        res_count = np.sum((live_col == 1) & (idx_col == 0))
        
        # Calculate log2 Relative Fitness (with safety for extinction)
        if res_count > 0 and sens_count > 0:
            fitness = np.log2(sens_count / res_count)
        elif sens_count == 0 and res_count > 0:
            fitness = -5.0 # Cap the graph if sensitive strain goes extinct
        elif res_count == 0 and sens_count > 0:
            fitness = 5.0  # Cap the graph if resistant strain goes extinct
        else:
            fitness = 0.0
            
        seed_fitness.append(fitness)
        
    all_fitness_trajectories.append(seed_fitness)

# ============================================================
# CALCULATE MEAN AND VARIANCE & PLOT
# ============================================================
if all_fitness_trajectories:
    # Ensure all arrays are the same length before averaging
    min_len = min(len(traj) for traj in all_fitness_trajectories)
    trimmed_trajectories = np.array([traj[:min_len] for traj in all_fitness_trajectories])
    
    mean_fit = np.mean(trimmed_trajectories, axis=0)
    std_fit = np.std(trimmed_trajectories, axis=0)
    time_steps = np.arange(min_len)

    plt.figure(figsize=(8, 5))
    
    plt.fill_between(time_steps, mean_fit - std_fit, mean_fit + std_fit, color='#256EFF', alpha=0.2)
    plt.plot(time_steps, mean_fit, color='#256EFF', linewidth=3, label='Mean Relative Fitness')
    
    # Add a horizontal line at 0 (the 1:1 survival baseline)
    plt.axhline(0, color='black', linestyle='--', linewidth=1.5, alpha=0.7, label='Equal Fitness Baseline')

    plt.title(f"Relative Susceptible Fitness Over Time ($C_0={C}, D={D}, A_0={A0}$)")
    plt.xlabel("Simulation Frames")
    plt.ylabel("Relative Fitness ($\log_2 \dfrac{N_{sens}}{N_{res}}$)")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()

    plot_filename = RESULTS_DIR / "Fitness_Trajectory.png"
    plt.savefig(plot_filename, dpi=300)
    print(f"\nSuccess! Saved trajectory to {plot_filename}")
else:
    print("No data was loaded.")