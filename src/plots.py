from matplotlib import pyplot as plt
import numpy as np

import data


def show_plots():
    plt.show()


def create_heatmap_plots():
    plots = []
    for sim_id, sim_matrix in data.sim_matrices.items():
        fig, ax = plt.subplots()
        ax.set_title(f"Similarity heatmap: {sim_id}")
        
        im = ax.imshow(sim_matrix, cmap="viridis", interpolation="nearest")
        fig.colorbar(im, ax=ax)

        if data.NUM_DIRS > 15:
            ax.axis("off")
        else:
            labels = range(1, data.NUM_DIRS + 1)
            ticks = [t for t in range(0, len(data.files), data.NUM_FILES_PER_DIR)]
            ax.set_xticks(ticks, labels)
            ax.set_yticks(ticks, labels)
        fig.tight_layout()
        
        plots.append((fig, ax))
    
    return plots


def create_fscores_plot():
    fig, ax = plt.subplots()
    ax.set_title("F-scores per tool")
    
    ax.set_xlabel("Similarity threshold")
    ax.set_ylabel("F-score")
    
    
    thresholds = np.arange(0.1, 1, 0.1)         
    for sim_id, sim_matrix in data.sim_matrices.items():
        # Calculate F-scores (use upper triangle of the matrix for symmetric matrices)
        fscores = [data.get_fscore(np.triu(sim_matrix) if sim_matrix.isSymmetric else sim_matrix, t) for t in thresholds]
        ax.plot(thresholds, fscores, label=sim_id)
        
    ax.legend()
    return fig, ax