import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import glob
import os

st.set_page_config(layout="wide")
st.title("IIoT Chromosome Visualization (Unified Grayscale)")

# ---------------------------------------------------------
# Unified 4-level grayscale palette
# ---------------------------------------------------------
gray_colors = ["#000000", "#555555", "#AAAAAA", "#DDDDDD"]

cpu_colors = gray_colors        # 0~3 그대로
mem_colors = gray_colors        # 0/1 → 0/3 매핑
off_colors = gray_colors        # 0/1 → 0/3 매핑


# ---------------------------------------------------------
# Draw one horizontal chromosome strip
# ---------------------------------------------------------
def draw_strip(ax, values, cmap, title):
    for i, v in enumerate(values):
        ax.add_patch(patches.Rectangle((i,0), 1, 1, facecolor=cmap[v]))
    ax.set_xlim(0, len(values))
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])
    if title:
        ax.set_title(title, fontsize=13)


# ---------------------------------------------------------
# Parse task file (4 values per line)
# mem_idx, cpu_idx, cloud_idx, off_idx
# ---------------------------------------------------------
def parse_task_file(path):
    cpu_vals = []
    mem_vals = []
    off_vals = []

    with open(path) as f:
        for line in f:
            if line.startswith("#") or len(line.strip()) == 0:
                continue

            mem_idx, cpu_idx, cloud_idx, off_idx = map(int, line.split())

            # MEM: 0→0, 1→3
            mem_mapped = 0 if mem_idx == 0 else 3

            # OFF: 0→0, 1→3
            off_mapped = 0 if off_idx == 0 else 3

            cpu_vals.append(cpu_idx)      # already 0~3
            mem_vals.append(mem_mapped)
            off_vals.append(off_mapped)

    return cpu_vals, mem_vals, off_vals


# ---------------------------------------------------------
# Algorithm order (reversed as requested)
# ---------------------------------------------------------
algorithms  = ["co-dmo-ct", "co-dmo", "offloading", "dvs", "baseline"]
algo_names = ["CO-DMO-CT", "CO-DMO", "Offloading", "DVS", "Baseline"]


# ---------------------------------------------------------
# Workload tabs
# ---------------------------------------------------------
workloads = ["0.1","0.2","0.3","0.4","0.5","0.6","0.7","0.8","0.9"]
tabs = st.tabs(workloads)

for w_idx, w in enumerate(workloads):
    with tabs[w_idx]:

        st.subheader(f"Workload = {w}")

        # Legend
        st.markdown("""
### Legend — Unified Grayscale Mapping  
- **0 (Darkest)** → Highest power / Faster 
- **3 (Lightest)** → Lowest power / Slower  

""")

        # Locate task directory
        pattern = f"tmp/output_{w}+*/task"
        dirs = glob.glob(pattern)

        if len(dirs) == 0:
            st.warning(f"No data found for workload {w}")
            continue

        task_dir = dirs[0]

        # Create 3×5 figure
        fig, axes = plt.subplots(3, 5, figsize=(22, 6))
        fig.tight_layout(pad=3)

        row_labels = ["CPU", "MEM", "OFFLOADING"]   # ← 추가

        # Fill columns by algorithm
        for col, algo in enumerate(algorithms):
            fname = f"{task_dir}/task_{w}+100+{algo}.txt"

            if not os.path.exists(fname):
                for r in range(3):
                    axes[r][col].axis("off")
                axes[0][col].set_title(f"{algo_names[col]} (missing)")
                continue

            cpu_vals, mem_vals, off_vals = parse_task_file(fname)

            draw_strip(axes[0][col], cpu_vals, cpu_colors, algo_names[col])
            draw_strip(axes[1][col], mem_vals, mem_colors, "")
            draw_strip(axes[2][col], off_vals, off_colors, "")

        # ← 여기: 각 row의 맨 왼쪽에 레이블 추가
        for r in range(3):
            axes[r][0].set_ylabel(row_labels[r],
                                fontsize=20,
                                rotation=0,     # 가로 텍스트
                                labelpad=80,    # strip에서 40px 왼쪽
                                va='center')
        st.pyplot(fig)
