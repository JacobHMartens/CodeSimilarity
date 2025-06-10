from functools import partial
from typing import Callable

import numpy as np

from data import File

type compFunc = Callable[[bytes], bytes]


def _complenght(data: bytes, compressor: compFunc) -> int:
    """
    Returns the length of the compressed data using the specified compressor.
    """
    return len(compressor(data))


def sim_C_NCD(files: list[File], compressor: compFunc) -> np.ndarray:
    """
    Computes the pairwise similarity of a list of files using Normalized Compression Distance (NCD) with the specified compressor.
    First parameter is a list of tuples where each tuple contains the filename and the bytes representing the file content.
    Second parameter is a compressor function.
    Returns a list of tuples containing the names of the compared files and their similarity score.
    """
    def NCD(x: bytes, y: bytes, compressor: compFunc) -> float:
        xy = x + y
        partial_compressed_size = partial(_complenght, compressor=compressor)
        Zx, Zy, Zxy = list(map(partial_compressed_size, [x, y, xy]))
        return (Zxy - min(Zx, Zy)) / max(Zx, Zy)
    
    size = len(files)
    similarities = np.zeros((size, size), dtype=float)
    for i in range(len(files)):
        file1 = files[i]
        for j in range(i, len(files)):
            file2 = files[j]
            sim = 1 - NCD(file1.get_bytes(), file2.get_bytes(), compressor)
            similarities[i, j] = sim
            if i != j:
                similarities[j, i] = sim
    return similarities

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
