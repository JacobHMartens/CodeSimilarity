from pathlib import Path
from collections import defaultdict

import numpy as np

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
    
    
class SimMatrix(np.ndarray):
    isSymmetric: bool = False
    xAxis: list[File] = None
    yAxis: list[File] = None


JAVA250_DATA_PATH: Path = Path("Project_CodeNet_Java250")
JAVA250_DATA: list[list[File]] = None
NUM_SAMPLE_DIRS: int = 0
NUM_SAMPLE_FILES: int = 0
NUM_CLASSIFICATION_DIRS: int = 0
NUM_TRAINING_FILES: int = 0
NUM_VALIDATION_FILES: int = 0
sample_files: list[File] = None
training_files: list[File] = None
validation_files: list[File] = None

classification_per_group_per_tool: dict = defaultdict(lambda: np.zeros((NUM_SAMPLE_DIRS, NUM_SAMPLE_DIRS), dtype=int))
sim_matrices: dict[str, SimMatrix] = {}

    
def load_java250_data():
    """
    Load the Java250 dataset as File objects. 
    The dataset is sorted for deterministic behavior.
    """
    global JAVA250_DATA

    all_dirs = sorted([dir for dir in JAVA250_DATA_PATH.iterdir() if dir.is_dir()], key=lambda d: d.name)  # All subdirectories sorted by name
    JAVA250_DATA = [[File(file, group=i) for file in dir.iterdir() if file.is_file()] for i, dir in enumerate(all_dirs)]
    map(lambda files: files.sort(key=lambda f: f.name), JAVA250_DATA)  # Sort files in each directory by name
 

def load_sample_data(num_dirs: int, num_files: int):
    """
    Load the first 'num_files' files from each of the first 'num_dirs' subdirectories.
    """
    global NUM_SAMPLE_DIRS, NUM_SAMPLE_FILES
    global sample_files
    
    NUM_SAMPLE_DIRS = num_dirs
    NUM_SAMPLE_FILES = num_files
    sample_files = [file for dir in JAVA250_DATA[:num_dirs] for file in dir[:num_files]]


def load_classification_data(num_dirs: int, num_training: int, num_validation: int):
    """
    Load the first 'num_training' files and the last 'num_validation' files from each 
    of the first 'num_dirs' subdirectories for classification.
    """
    global NUM_CLASSIFICATION_DIRS, NUM_TRAINING_FILES, NUM_VALIDATION_FILES
    global training_files, validation_files
    
    NUM_CLASSIFICATION_DIRS = num_dirs
    NUM_TRAINING_FILES = num_training
    NUM_VALIDATION_FILES = num_validation
    training_files = [file for dir in JAVA250_DATA[:NUM_CLASSIFICATION_DIRS] for file in dir[:NUM_TRAINING_FILES]]
    validation_files = [file for dir in JAVA250_DATA[:NUM_CLASSIFICATION_DIRS] for file in dir[-NUM_VALIDATION_FILES:]]
    

def get_fscore(sim_matrix: SimMatrix, threshold = 0.5):
    """
    Calculate the F-score for the similarity matrix.
    """
    # Reshape the similarity matrix into a matrix of sub-matrices, where each 
    # sub-matrix is the pairwise similarity of files within two directories.
    grouped_sim_matrix = \
        sim_matrix \
        .reshape(NUM_SAMPLE_DIRS, NUM_SAMPLE_FILES, NUM_SAMPLE_DIRS, NUM_SAMPLE_FILES) \
        .transpose(0, 2, 1, 3)
    
    # Extract the diagonal sub-matrices, which represent the pairwise 
    # similarity of files within the same directory.
    idx = np.arange(NUM_SAMPLE_DIRS)
    grouped_diagonal = grouped_sim_matrix[idx, idx]

    # True Positives: Similarity scores above the threshold within the diagonal
    # False Positives: Similarity scores above the threshould outside the diagonal
    # Actual Positives: Total number of similarity scores in the diagonal 
    true_positives = np.sum(grouped_diagonal > threshold) 
    false_positives = np.sum(sim_matrix > threshold) - true_positives  
    actual_positives = len(sample_files) * NUM_SAMPLE_FILES
    
    # Calculate precision, recall, and F-score    
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / actual_positives
    fscore = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return fscore

def cluster_matrices_by_groups(sim_matrix):  # TODO: Rework! Store sorting order in the matrix
    """
    Cluster similarity matrices based on file groups (subdirectories) such that the 
    higher average similarity within each group is closer to the top left corner.
    """
    # Group files by their group attribute
    group_to_indices = defaultdict(list)
    for idx, file in enumerate(sample_files):
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
    