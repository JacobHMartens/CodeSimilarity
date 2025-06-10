import os
from pathlib import Path
import shutil
import subprocess
import pandas as pd

def plag_jplag_java(file_paths: list) -> list:
    os.chdir(Path(os.path.dirname(__file__)).parent)
    # Create a temporary directory to store the files
    temp_dir = os.path.join(os.getcwd(), "temp")
    try:
        os.makedirs(temp_dir, exist_ok=True)
        # Copy the files to the temporary directory
        for file_path in file_paths:
            shutil.copy(file_path, temp_dir)

        # Run jplag tool
        subprocess.run(["java", "-jar", "./tools/jplag/jplag-6.1.0-jar-with-dependencies.jar", temp_dir, "--csv-export", "-M", "RUN"])

        # Read the output CSV file
        results_dir = os.path.join(os.getcwd(), "results")
        csv_file = os.path.join(results_dir, "results.csv")
        df = pd.read_csv(csv_file)

        # Extract similarity values
        similarity_values = df["averageSimilarity"].tolist()
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)

    return similarity_values
