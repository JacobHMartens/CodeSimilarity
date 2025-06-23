import os
from pathlib import Path
import shutil
import subprocess
import pandas as pd

from data import JAVA250

def plag_jplag_java(data: JAVA250) -> list:
    tools_dir = Path(os.path.dirname(__file__)).parent.parent
    os.chdir(tools_dir)
    temp_dir = data.make_subset_dir()
    
    try:
        # Run jplag tool
        res = subprocess.run(["java", "-jar", "./tools/jplag/jplag-6.1.0-jar-with-dependencies.jar", temp_dir, "--csv-export", "-M", "RUN"])
        if res.returncode != 0:
            raise Exception(f"JPlag execution failed with return code: {res.returncode}. Error message: {res.stderr.decode('utf-8')}")
        print("JPlag executed successfully. Results are saved in the 'results' directory.")
        
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
