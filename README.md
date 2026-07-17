# Analysis-scripts-for-Individual-based-model---Bacterial-colony-dynamics

This repository contains the Python analysis pipeline used to quantify the spatiotemporal dynamics of bacterial colonies under antibiotic stress.

We used a hybrid, off-lattice Individual-Based Model (IbM). It is off-lattice because cell positions are tracked in continuous space using overdamped Langevin dynamics, and it is 'hybrid' because we couple these discrete, mechanically interacting agents with continuous reaction-diffusion PDEs to solve the chemical microenvironment."

While the core simulation engine is proprietary/withheld and remains associated with the TCBP Lab @IISER TVM, these scripts demonstrate the complete downstream processing pipeline: extracting physical metrics (roughness, nematic order, clustering) from raw spatial coordinates and generating visualisations.

## 🗂️ Pipeline Architecture

The workflow is divided into two distinct phases:

### Phase 1: Spatial & Statistical Extraction (`scripts/01_extraction/`)
These scripts parse raw simulation frames (`.xyz` and `.pkl` binaries) to compute structural and biological metrics:
* **Active Layer Profiling:** Calculates the active layer depth ($\delta$) and tracks boundary diffusion gradients over time.
* **Morphological Tracking:** Extracts cell lengths ($lf$) and computes probability density distributions (KDE) for sensitive vs resistant strains.
* **Surface Roughness:** Slices the colony boundary into discrete vertical bins to measure the standard deviation of leading-edge coordinates.
* **Cluster Identification (PBC):** Utilises `scipy.spatial.cKDTree` to perform fast, distance-based spatial clustering of rod-shaped bacteria across Periodic Boundary Conditions (PBC), mitigating the $O(N^2)$ computational cost of identifying contiguous cell networks.

### Phase 2: Visualisation (`scripts/02_visualisation/`)
These scripts ingest the processed `.txt` files to generate standardised, comparative plots across varying nutrient environments ($C_0, D$) and antibiotic concentrations ($A_0$):
* Density distributions of Cell Lengths and Nematic Order parameters.
* Trajectory tracking for Mean Aspect Ratios and Relative Susceptible Fitness ($\log_2 \dfrac{N_{sens}}{N_{res}}$) prior to competitive exclusion/extinction.
* Log-scaled comparisons of Mean Cluster Size against antibiotic stress.
