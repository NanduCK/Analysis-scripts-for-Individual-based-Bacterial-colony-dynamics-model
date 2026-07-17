#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pickle
import sys
import matplotlib.pyplot as plt
from scipy.spatial import cKDTree
from collections import defaultdict
from config import RAW_DATA_DIR, PROCESSED_DATA_DIR

# ============================================================
# Periodic boundary utilities
# ============================================================

def minimum_image(vec, box):
    return vec - box * np.round(vec / box)

# ============================================================
# Geometry: distance between two line segments (no PBC)
# ============================================================

def segment_segment_distance(p1, q1, p2, q2):
    """
    Minimum distance between two finite line segments in 2D
    """
    u = q1 - p1
    v = q2 - p2
    w0 = p1 - p2

    a = np.dot(u, u)
    b = np.dot(u, v)
    c = np.dot(v, v)
    d = np.dot(u, w0)
    e = np.dot(v, w0)

    denom = a * c - b * b
    eps = 1e-12

    if denom < eps:  # parallel or nearly parallel
        s = 0.0
        t = np.clip(e / c if c > eps else 0.0, 0.0, 1.0)
    else:
        s = (b * e - c * d) / denom
        t = (a * e - b * d) / denom
        s = np.clip(s, 0.0, 1.0)
        t = np.clip(t, 0.0, 1.0)

    closest1 = p1 + s * u
    closest2 = p2 + t * v

    return np.linalg.norm(closest1 - closest2)

# ============================================================
# Closest distance between two rods with PBC
# ============================================================

def closest_distance_between_rods_pbc(r1, u1, L1, r2, u2, L2, box):
    """
    Minimum distance between two rods (finite line segments) in 2D with PBC
    """

    # minimum-image displacement
    r12 = minimum_image(r2 - r1, box)
    r2_img = r1 + r12

    # endpoints of rod 1
    p1 = r1 - 0.5 * L1 * u1
    q1 = r1 + 0.5 * L1 * u1

    # endpoints of rod 2 (image)
    p2 = r2_img - 0.5 * L2 * u2
    q2 = r2_img + 0.5 * L2 * u2

    return segment_segment_distance(p1, q1, p2, q2)

# ============================================================
# Graph construction
# ============================================================

def build_graph_rods_pbc(positions, orientations, lengths, cutoff, box):
    N = len(positions)
    graph = defaultdict(list)
    
    if N == 0:
        return graph

    # Find the maximum possible reach of any rod
    max_L = np.max(lengths)
    
    # A safe search radius for the centers: maximum half-lengths plus the cutoff
    search_radius = max_L + cutoff

    # Build a spatial tree using periodic boundary conditions
    tree = cKDTree(positions, boxsize=box)

    # Query the tree for ALL pairs whose centers are within the search radius
    # This replaces the O(N^2) double loop with an O(N log N) spatial search
    candidate_pairs = tree.query_pairs(r=search_radius)

    # Now, ONLY run the expensive rod-geometry math on these nearby candidates
    for i, j in candidate_pairs:
        dist = closest_distance_between_rods_pbc(
            positions[i], orientations[i], lengths[i],
            positions[j], orientations[j], lengths[j], box)
        
        if dist <= cutoff:
            graph[i].append(j)
            graph[j].append(i)

    return graph

# ============================================================
# Cluster identification - (DFS)iterative
# ============================================================

def find_clusters(graph, N):
    visited = [False] * N
    clusters = []

    def dfs(i, cluster):
        visited[i] = True
        cluster.append(i)
        for j in graph[i]:
            if not visited[j]:
                dfs(j, cluster)

    for i in range(N):
        if not visited[i]:
            cluster = []
            dfs(i, cluster)
            clusters.append(cluster)

    return clusters
# In[26]:


# ============================================================
# MAIN: Ensemble averaging
# ============================================================

lint = 4                         # number of Seeds
box_size = np.array([200.0, 400.0]) #box-size

ID = []
MC = []    # mean cluster size
LC = []    # largest cluster size

for w in range(1, lint + 1):

    C, D = 100, 10
    filepath = RAW_DATA_DIR / f"C0-{C},D-{D}" / f"SEED{w}" / "datas.pkl"
    
    with open(filepath, "rb") as f:
        data = pickle.load(f)

    # reading the last dataframe
    data = data[:-1]

    frame = np.array(data[-1])
    idx = frame[:, 1]
    rx = frame[:, 2]    #posittions
    ry = frame[:, 3]
    ex = frame[:, 5]    #orientations
    ey = frame[:, 6]
    d   = frame[:, 11]    #diameter
    L   = frame[:, 10]    #length
    live = frame[:,15]
    # select rods (idx == 2)
    mask = (idx == 1) & (live == 1)  #idx = 0 for resistant, and idx = 1 for sensitive

    if np.sum(mask) == 0:
        print(f"Seed {w}: No living sensitive cells remaining. Assigning 0 to clusters.")
        ID.append(w)
        MC.append(0.0)
        LC.append(0.0)
        continue

    positions = np.stack([rx[mask], ry[mask]], axis=1) % box_size
    orientations = np.stack([ex[mask], ey[mask]], axis=1)
    lengths = L[mask]

    # normalize orientations (safety)
    orientations /= np.linalg.norm(orientations, axis=1)[:, None]

    # cutoff = rod diameter (or slightly larger)
    cutoff = 1.2 * np.mean(d[mask]) 

    # build clusters
    graph = build_graph_rods_pbc(
        positions, orientations, lengths, cutoff, box_size
    )
    clusters = find_clusters(graph, len(positions))

    cluster_sizes = np.array([len(c) for c in clusters])

   
    mean_cluster_size = np.sum(cluster_sizes**2) / np.sum(cluster_sizes)
    largest_cluster_size = np.max(cluster_sizes)

    ID.append(w)
    MC.append(mean_cluster_size)
    LC.append(largest_cluster_size)

# ============================================================
# Save results
# ============================================================

ID = np.array(ID)
MC = np.array(MC)
LC = np.array(LC)

np.savetxt(
    PROCESSED_DATA_DIR / "Cluster_Size.txt",
    np.column_stack((ID, MC)),
    delimiter="\t",
    header="ID\tMeanClusterSize"
)

avg_MC = np.mean(MC)
avg_LC = np.mean(LC)
sem_MC = np.std(MC, ddof=1) / np.sqrt(len(MC))

np.savetxt(
    PROCESSED_DATA_DIR / "Cluster_summary.txt",
    np.array([[avg_MC, avg_LC, sem_MC]]),
    delimiter="\t",
    header="avg_MC\tavg_LC\tsem_MC"
)

print("Done.")
print(f"Average mean cluster size = {avg_MC:.3f}")
print(f"Average largest cluster   = {avg_LC:.3f}")
print(f"SEM of mean cluster size  = {sem_MC:.3f}")



# In[23]:




