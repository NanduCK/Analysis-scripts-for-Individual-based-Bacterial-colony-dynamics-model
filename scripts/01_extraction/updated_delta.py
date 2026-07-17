import numpy as np
import pandas as pd
import os
from config import RAW_DATA_DIR, PROCESSED_DATA_DIR
# ============================================================
# CONSTANTS & SETUP
# ============================================================
D = 200
C = 150
k = 6
r = 0.5
l = 3.0

# Calculate Area once outside the loop
A = (np.pi * r**2) + (2 * l * r)

Boundry = []
Active_Layer = []

# ============================================================
# MAIN EXECUTION
# ============================================================
for S in range(1, 2):
    height = []
    x_m = np.linspace(200, 400, 100)
    
    T = 1
    while True:
     
        file_path = RAW_DATA_DIR / f"C0-{C},D-{D}" / f"data_{T}.txt"
        
        if not file_path.exists():
            print(f"Finished processing. Found {T-1} total frames.")
            break 

        # Read Data
        Grad = pd.read_fwf(file_path, names=["x", "y", "Conc"])

        # Filter diffusion data for one side
        grad = Grad[(Grad['y'] >= 100)]         
        Conc = grad['Conc'].to_numpy()

        # Reshape into grid instantly
        Z_grad = Conc.reshape(100, 100)
        Z_grad_mean = np.mean(Z_grad, axis=0)
        
        max_val = np.max(Z_grad_mean)

       
        if max_val > 0:
            # np.argmax finds the exact indices instantly
            h_idx = np.argmax(Z_grad_mean >= max_val * 0.5)
            w_idx = np.argmax(Z_grad_mean >= max_val * 0.01)

            # Prevent negative or zero heights from bad array indexing
            current_height = x_m[h_idx] - x_m[w_idx]
            if current_height > 0:
                height.append(current_height)

    # ============================================================
    # SAFE MEDIAN CALCULATION
    # ============================================================
    if height:
        H = np.median(height)
        print(f"Median of list is : {H:.4f}")
        
        # Calculate Active Layer Depth
        Num = D * C
        Dnum = (H**2) * k * A
        
        delta = np.sqrt(Num / Dnum)

        Boundry.append(H)
        Active_Layer.append(delta)
    else:
        print(f"Warning: No valid gradient found for this environment.")

# Save the output
np.savetxt(PROCESSED_DATA_DIR / "Delta.txt", np.column_stack((Boundry, Active_Layer)), delimiter="   ", fmt='%.6f')
print("Successfully generated Delta.txt")