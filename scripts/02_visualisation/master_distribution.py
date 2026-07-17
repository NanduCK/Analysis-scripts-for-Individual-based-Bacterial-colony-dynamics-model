import numpy as np
import matplotlib.pyplot as plt
import os
import matplotlib.cm as cm
from config import PROCESSED_DATA_DIR, RESULTS_DIR, CD_to_delta
# ============================================================
# 1. SETUP & PARAMETERS
# ============================================================


# The specific antibiotic concentration to analyze 
A0_target = 0.01  
num_seeds = 4
prefix = "" 

# Sort environments from starved to rich
sorted_envs = sorted(CD_to_delta.items(), key=lambda item: item[1])


plt.rcParams.update({
    'font.size': 14,          
    'axes.titlesize': 16,     
    'axes.labelsize': 16,     
    'xtick.labelsize': 12,    
    'ytick.labelsize': 12,    
    'legend.fontsize': 12,    
    'legend.title_fontsize': 14 
})

print(f"Aggregating KDE data across environments for A0={A0_target}...")

# ============================================================
# 2. EXTRACT DATA & PLOT
# ============================================================
plt.figure(figsize=(10, 6))
colors = cm.viridis(np.linspace(0, 0.9, len(sorted_envs)))

for idx, ((C, D), delta) in enumerate(sorted_envs):
    all_y_kde = []
    x_kde = None
    
    # Path to the specific condition's folder
    base_path = PROCESSED_DATA_DIR / f"C0-{C},D-{D}" / f"C0-{C},D-{D},A0-{A0_target}"
    for seed in range(1, num_seeds + 1):
        kde_file = base_path / f"KDE{prefix}_{seed}.txt"
        
        if os.path.exists(kde_file):
            kde_data = np.loadtxt(kde_file)
            
            # Grab the X-axis from the first valid file
            if x_kde is None:
                x_kde = kde_data[:, 0]
                
            all_y_kde.append(kde_data[:, 1])
        else:
            print(f"Warning: {kde_file} missing. Skipping.")

    # Calculate the mean across the seeds for this specific environment
    if len(all_y_kde) > 0:
        all_y_kde = np.array(all_y_kde)
        mean_kde = np.mean(all_y_kde, axis=0)
        
        # Plot the mean line for this delta
        label_str = fr'$\delta$ = {delta}  ($C_0$={C}, $D$={D})'
        plt.plot(x_kde, mean_kde, color=colors[idx], linewidth=2.5, label=label_str)
    else:
        print(f"Error: No data loaded for C0={C}, D={D}")

# ============================================================
# 3. STYLING & SAVING
# ============================================================
plt.title(fr"Sensitive Cell Length Distribution under Antibiotic Stress ($A_0$={A0_target})", fontweight='bold')
plt.xlabel(r"Cell Length ($\mu m$)", fontweight='bold')
plt.ylabel("Probability Density", fontweight='bold')

# Moving the legend outside to keep the plot area clean
plt.legend(title=r"Active Layer ($\delta$) & Environment", bbox_to_anchor=(1.05, 1), loc='upper left')

plt.grid(True, linestyle='--', alpha=0.5)

# Restrict the X-axis to the biologically relevant length (e.g., 0 to 6 micrometers)
# To prevent the graph from zooming out too far if there are weird outliers
plt.xlim(0, 6) 

plt.tight_layout()

# Save the plot
plot_filename = RESULTS_DIR / f"Combined_Length_Distribution_A0-{A0_target}.png"
plt.savefig(plot_filename, dpi=300)
print(f"Success! Saved averaged master graph to {plot_filename}")