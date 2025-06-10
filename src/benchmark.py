from pathlib import Path
import argparse
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from data import Data, File
from similarity import *
from tools.compressors import *

type simCFunc = Callable[[list[File]], np.ndarray]


def generate_simC_matrix(simC: simCFunc, compressor: compFunc, data: Data, clustered=False):
    """
    Generate a similarity matrix using the specified tool (simCFunc) and the provided data.
    """
    if not data.files:
        data.load_files()
    
    similarities = simC(data.files, compressor)
    x_labels = y_labels = list(map(str, data.files))
    
    if clustered:
        # Group files by their group attribute
        from collections import defaultdict
        group_to_indices = defaultdict(list)
        for idx, f in enumerate(data.files):
            group_to_indices[getattr(f, "group", 0)].append(idx)
        
        # Sort groups
        sorted_groups = sorted(group_to_indices.keys())
        new_order = []
        for group in sorted_groups:
            indices = group_to_indices[group]
            # For each group, sort indices by their average similarity (descending)
            avg_sims = [(i, np.mean(similarities[i, indices])) for i in indices]
            sorted_indices = [i for i, _ in sorted(avg_sims, key=lambda x: -x[1])]
            new_order.extend(sorted_indices)
        
        # Reorder matrix and labels
        similarities = similarities[np.ix_(new_order, new_order)]
        x_labels = [x_labels[i] for i in new_order]
        y_labels = [y_labels[i] for i in new_order]

    return similarities, x_labels, y_labels

    
def plot_heat_map(sim_matrix, x_labels=None, y_labels=None):
    """
    Plot a heat map of the similarity matrix.
    """
    plt.figure(figsize=(8, 8))
    plt.imshow(sim_matrix, cmap="viridis", interpolation="nearest")
    plt.title("Similarity Heat Map")
    plt.colorbar()
    
    if x_labels is not None and y_labels is not None:
        x_ticks = list(range(len(x_labels)))
        y_ticks = list(range(len(y_labels)))
        plt.xticks(x_ticks, x_labels, rotation=90)
        plt.yticks(y_ticks, y_labels)
    else:
        plt.axis('off')
    plt.show()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-dirs", type=int, help="Number of sample directories to process.")
    parser.add_argument("--num-files", type=int, help="Number of files to process in each directory.")
    return parser.parse_args()


if __name__ == "__main__":
    example_codenet_samples_dir = Path("samples/Project_CodeNet_Java250")
    args = parse_args()
    print(args.num_dirs, args.num_files)
    data = Data(
        num_dirs=args.num_dirs, 
        num_files=args.num_files, 
        samples_dir=example_codenet_samples_dir
    )
   
    sim_matrix, x_labels, y_labels = generate_simC_matrix(
        simC=sim_C_NCD, 
        compressor=comp_bzip2, 
        data=data,
        clustered=True
    )
    # plot_heat_map(sim_matrix, x_labels, y_labels)
    plot_heat_map(sim_matrix, None, None)  # Plot without labels
    
