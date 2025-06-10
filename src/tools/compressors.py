import bz2
import zlib
import gzip
import zstandard
import zstd

def comp_zstd(data: bytes, level: int=3) -> bytes:
    if level not in range(1, 23):
        raise ValueError("Compression level out of range. zstd accepts compression levels in the range 1 to 22.")
    compressed_file = zstd.compress(data, level)
    return compressed_file

def comp_zstandard(data: bytes, level: int=22) -> bytes:
    if level not in range(1, 23):
        raise ValueError("Compression level out of range. zstandard accepts compression levels in the range 1 to 22.")
    compressed_file = zstandard.compress(data, level)
    return compressed_file

def comp_zlib(data: bytes, level: int=9) -> bytes: 
    if level not in range(1, 10):
        raise ValueError("Compression level out of range. zlib accepts compression levels in the range 1 to 9.")
    compressed_file = zlib.compress(data, level)
    return compressed_file

def comp_gzip(data: bytes, level: int=9) -> bytes:
    if level not in range(1, 10):
        raise ValueError("Compression level out of range. gzip accepts compression levels in the range 1 to 9.")
    compressed_file = gzip.compress(data, level)
    return compressed_file

def comp_bzip2(data: bytes, level: int=9) -> bytes:
    if level not in range(1, 10):
        raise ValueError("Compression level out of range. bzip2 accepts compression levels in the range 1 to 9.")
    compressed_file = bz2.compress(data, level)
    return compressed_file