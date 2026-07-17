import numpy as np
import matplotlib.pyplot as plt
import os
import matplotlib.cm as cm
from config import PROCESSED_DATA_DIR, RESULTS_DIR, CD_to_delta
# ============================================================
# PARAMETERS & DELTA MAPPING
# ============================================================


A0_values = [0.005, 0.01, 0.05, 0.1, 0.2, 0.4]
file_to_load = "Roughness.txt" 
metric_name = "Roughness"

# ============================================================
# SORT THE ENVIRONMENTS BY DELTA
# ============================================================
sorted_envs = sorted(CD_to_delta.items(), key=lambda item: item[1])

print(f"Plotting {metric_name} vs A0 with combined legend...")

# ============================================================
# EXTRACT DATA AND PLOT
# ============================================================
plt.figure(figsize=(11, 6))

x_indices = np.arange(len(A0_values))
colors = cm.viridis(np.linspace(0, 0.9, len(sorted_envs)))

for idx, ((C, D), delta) in enumerate(sorted_envs):
    means_for_env = []
    stds_for_env = []
    
    for A0 in A0_values:
        filepath = PROCESSED_DATA_DIR / f"C0-{C},D-{D}" / f"C0-{C},D-{D},A0-{A0}" / file_to_load

        if filepath.exists():
            data = np.loadtxt(filepath, skiprows=1)
            vals = data[:, 1]
            means_for_env.append(np.mean(vals))
            stds_for_env.append(np.std(vals))
        else:
            means_for_env.append(np.nan)
            stds_for_env.append(np.nan)
            
   
    combined_label = fr'$\delta$ = {delta}  ($C_0$={C}, $D$={D})'
    
    plt.errorbar(x_indices, means_for_env, yerr=stds_for_env, fmt='-o', 
                 color=colors[idx], linewidth=2.5, markersize=7, capsize=4, 
                 label=combined_label)

# ============================================================
# FORMATTING
# ============================================================
plt.title(fr"Colony {metric_name} vs. Antibiotic Stress Across Environments")
plt.xlabel(r"Antibiotic Concentration ($A_0$)")
plt.ylabel(fr"Mean {metric_name}")
plt.xticks(x_indices, A0_values)


plt.legend(title=r"Active Layer ($\delta$) & Environment", 
           bbox_to_anchor=(1.05, 1), loc='upper left')

plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()

output_filename = RESULTS_DIR / f"{metric_name}_vs_A0_Combined_Legend.png"
plt.savefig(output_filename, dpi=300)
print(f"Success! Saved {output_filename}")