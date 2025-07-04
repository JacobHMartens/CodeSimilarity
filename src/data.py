from pathlib import Path
from collections import defaultdict

import numpy as np

class SimMatrix(np.ndarray):
    isSymmetric: bool = False

class File:
    name: str
    path: Path
    group: int = -1
    _bytes: bytes = None
    
    def __init__(self, path: Path, group: int = -1):
        if not path.is_file():
            raise ValueError(f"Path {path} is not a file.")
        self.path = path
        self.name = path.name
        self.group = group
        
    def __str__(self):
        return f"{self.group}_{self.name}"
    
    def get_bytes(self) -> bytes:
        if self._bytes is None:
            self._bytes = self.path.read_bytes()
        return self._bytes


JAVA250_DATA_PATH: Path = Path("Project_CodeNet_Java250")
NUM_DIRS: int = 0
NUM_FILES_PER_DIR: int = 0
files: list[File] = []
subdirs: list[Path] = []

sim_matrices: dict[str, SimMatrix] = {}

    
def load_java250_data(num_dirs: int, num_files: int):
    """
    Load the first 'num_files' files from the first 'num_dirs' subdirectories.
    """
    global NUM_DIRS, NUM_FILES_PER_DIR, subdirs, files
    NUM_DIRS = num_dirs
    NUM_FILES_PER_DIR = num_files
    
    files.clear()
    subdirs = sorted([dir for dir in JAVA250_DATA_PATH.iterdir() if dir.is_dir()])[:num_dirs]
    for i, subdir in enumerate(subdirs):
        dir_files = sorted([file for file in subdir.iterdir() if file.is_file()])[:num_files]
        files.extend(map(lambda file: File(file, group=i), dir_files))
        

def get_fscore(sim_matrix: np.ndarray, threshold = 0.5):
    """
    Calculate the F-score for the similarity matrix.
    """
    # Reshape the similarity matrix into a matrix of sub-matrices, where each 
    # sub-matrix is the pairwise similarity of files within two directories.
    grouped_sim_matrix = \
        sim_matrix \
        .reshape(NUM_DIRS, NUM_FILES_PER_DIR, NUM_DIRS, NUM_FILES_PER_DIR) \
        .transpose(0, 2, 1, 3)
    
    # Extract the diagonal sub-matrices, which represent the pairwise 
    # similarity of files within the same directory.
    idx = np.arange(NUM_DIRS)
    grouped_diagonal = grouped_sim_matrix[idx, idx]

    # True Positives: Similarity scores above the threshold within the diagonal
    # False Positives: Similarity scores above the threshould outside the diagonal
    # Actual Positives: Total number of similarity scores in the diagonal 
    true_positives = np.sum(grouped_diagonal > threshold) 
    false_positives = np.sum(sim_matrix > threshold) - true_positives  
    actual_positives = len(files) * NUM_FILES_PER_DIR
    
    # Calculate precision, recall, and F-score    
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / actual_positives
    fscore = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return fscore

def cluster_matrices_by_groups(sim_matrix):  # TODO: Rework
    """
    Cluster similarity matrices based on file groups (subdirectories) such that the 
    higher average similarity within each group is closer to the top left corner.
    """
    # Group files by their group attribute
    group_to_indices = defaultdict(list)
    for idx, file in enumerate(files):
        group_to_indices[file.group].append(idx)
    
    # Sort groups
    sorted_groups = sorted(group_to_indices.keys())
    new_order = []
    for group in sorted_groups:
        indices = group_to_indices[group]
        # For each group, sort indices by their average similarity (descending)
        avg_sims = [(i, np.mean(sim_matrix[i, indices])) for i in indices]
        sorted_indices = [i for i, _ in sorted(avg_sims, key=lambda x: -x[1])]
        new_order.extend(sorted_indices)
    
    # Reorder matrix and labels
    sim_matrix = sim_matrix[np.ix_(new_order, new_order)]
    # x_labels = [x_labels[i] for i in new_order]
    # y_labels = [y_labels[i] for i in new_order]
    
    return sim_matrix#, x_labels, y_labels