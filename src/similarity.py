from functools import partial
from typing import Callable
import concurrent.futures

import numpy as np

from data import File

type compFunc = Callable[[bytes], bytes]


def _complenght(data: bytes, compressor: compFunc) -> int:
    """
    Returns the length of the compressed data using the specified compressor.
    """
    return len(compressor(data))

# helper to compute compressed lengths for a batch of pairs
def _batch_complengths(pairs: list[tuple[int,int,bytes]], compressor: compFunc) -> list[tuple[int,int,int]]:
    results = []
    for i, j, data in pairs:
        results.append((i, j, len(compressor(data))))
    return results

def sim_C_NCD(files: list[File], compressor: compFunc) -> np.ndarray:
    """
    Computes the pairwise similarity of a list of files using Normalized Compression Distance (NCD) with the specified compressor.
    First parameter is a list of File objects.
    Second parameter is a compressor function.
    Returns a similarity matrix.
    """
    
    def get_all_compressed_lengths(files: list[File], compressor: compFunc):
        """
        Returns a dictionary mapping file names to their compressed lengths. 
        Includes all pairwise combinations.
        """
        compressed_file_lengths = list(map(lambda file: _complenght(file.get_bytes(), compressor), files))
        compressed_pair_lengths = np.zeros((len(files), len(files)), dtype=int)
        # Batch-based parallel computation of pairwise compressed lengths
        # prepare all pairs
        pairs = [(i, j, files[i].get_bytes() + files[j].get_bytes())
                 for i in range(len(files)) for j in range(i, len(files))]
        batch_size = 100
        batches = [pairs[k:k+batch_size] for k in range(0, len(pairs), batch_size)]
        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = [executor.submit(_batch_complengths, batch, compressor) for batch in batches]
            for future in concurrent.futures.as_completed(futures):
                for i, j, val in future.result():
                    compressed_pair_lengths[i, j] = val
                    if i != j:
                        compressed_pair_lengths[j, i] = val
        # Alternative to the above 2 lines (similar running time):
        # compressed_pair_lengths += compressed_pair_lengths.T - np.diag(np.diag(compressed_pair_lengths))  # Make it symmetric (copy upper triangle to lower triangle)
        
        return compressed_file_lengths, compressed_pair_lengths
        
    def generate_similarity_matrix(compressed_file_lengths, compressed_pair_lengths):
        """
        Generates a similarity matrix based on NCD.
        """
        max_compressed_length_matrix = np.maximum.outer(compressed_file_lengths, compressed_file_lengths)
        min_compressed_length_matrix = np.minimum.outer(compressed_file_lengths, compressed_file_lengths)
        
        sim_matrix = 1 - (compressed_pair_lengths - min_compressed_length_matrix) / max_compressed_length_matrix
        return sim_matrix
    
    compressed_file_lengths, compressed_pair_lengths = get_all_compressed_lengths(files, compressor)
    return generate_similarity_matrix(compressed_file_lengths, compressed_pair_lengths)

def sim_C_ICD(files: list[File], compressor: compFunc) -> np.ndarray:
    """
    Computes the pairwise similarity of a list of files using Inclusion Compression Divergence (ICD) with the specified compressor.
    First parameter is a list of tuples where each tuple contains the filename and the bytes representing the file content.
    Second parameter is a compressor function.
    Returns a list of tuples containing the names of the compared files and their similarity score.
    """
    def ICD(x: bytes, y: bytes, compressor: compFunc) -> float:
        xy = x + y
        partial_compressed_size = partial(_complenght, compressor=compressor)
        Zx, Zy, Zxy = list(map(partial_compressed_size, [x, y, xy]))
        return (Zxy - Zy) / Zx
    
    size = len(files)
    similarities = np.zeros((size, size), dtype=float)
    for i in range(len(files)):
        file1 = files[i]
        for j in range(len(files)):
            file2 = files[j]
            sim = 1 - ICD(file1.get_bytes(), file2.get_bytes(), compressor)
            similarities[i, j] = sim
    return similarities
