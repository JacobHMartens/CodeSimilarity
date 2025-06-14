from dataclasses import dataclass, field
import os
import tempfile
import shutil
from pathlib import Path

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


class Data:
    num_dirs: int
    num_files: int
    samples_dir: Path
    temp_dir: Path = None
    files: list[File] = []
    subdirs: list[Path] = []
    
    def __init__(self, num_dirs: int, num_files: int, samples_dir: Path):
        self.num_dirs = num_dirs
        self.num_files = num_files
        self.samples_dir = samples_dir.absolute()
        
        if not self.samples_dir.is_dir():
            raise ValueError(f"Samples directory {self.samples_dir} does not exist or is not a directory.")
                    
    def load_files(self):
        """
        Load the first num_files files from each subdirectory. Load the subdirectories as well.
        """
        self.subdirs = sorted([dir for dir in self.samples_dir.iterdir() if dir.is_dir()])[:self.num_dirs]
        for i, subdir in enumerate(self.subdirs):
            files = sorted([file for file in subdir.iterdir() if file.is_file()])[:self.num_files]
            self.files.extend(map(lambda file: File(file, group=i), files))
        
    def make_subset_dir(self):
        """
        Create a temp directory containing only the first num_dirs subdirectories and the first num_files files in each subdirectory. 

        Returns the Path to that temp dir. You can pass it to your lib, then cleanup
        with shutil.rmtree(temp_dir).
        """
        # 1) create a temp directory
        self.temp_dir = Path(tempfile.mkdtemp(dir=self.samples_dir.parent))
            
        if not self.files:
            self.load_files()

        # 2) for each file, create a link in a new subdir
        for file in self.files:
            # Get the subdir for the target file
            subdir = self.subdirs[file.group]
            # Create the target subdir in the temp directory
            target_subdir = self.temp_dir / subdir.name
            target_subdir.mkdir(exist_ok=True)
            
            # Create a hard link or symlink to the file in the target subdir
            link_path = target_subdir / file.name
            try:
                os.link(file.path, link_path)
            except (OSError, NotImplementedError):
                # fall back to symlink
                os.symlink(file.path, link_path)
        
        return self.temp_dir