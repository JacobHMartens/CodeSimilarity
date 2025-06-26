import subprocess

def run_commands():
    commands = [
        # "py -m cProfile -o HeatFscores.prof src/main.py 5 300 -c bzip2 gzip zlib zstd zstandard -NCD -PH -PF",
        "py -m cProfile -o classify.prof src/main.py 5 200 -c bzip2 gzip -NCD -CLFY -ncf 100 -cs bm -PC",
        "py -m cProfile -o classify.prof src/main.py 5 200 -c zlib zstd zstandard -NCD -CLFY -ncf 100 -cs bm -PC",
        "py -m cProfile -o classify.prof src/main.py 5 200 -c bzip2 gzip -NCD -CLFY -ncf 100 -cs ha -PC",
        "py -m cProfile -o classify.prof src/main.py 5 200 -c zlib zstd zstandard -NCD -CLFY -ncf 100 -cs ha -PC",
        "py -m cProfile -o classify.prof src/main.py 5 200 -c bzip2 gzip -NCD -CLFY -ncf 100 -cs knn10 -PC",
        "py -m cProfile -o classify.prof src/main.py 5 200 -c zlib zstd zstandard -NCD -CLFY -ncf 100 -cs knn10 -PC"
    ]
    
    processes = []
    for i, cmd in enumerate(commands):
        print("Running command with id=%d: %s" % (i, cmd))
        process = subprocess.Popen(cmd.split())
        processes.append(process)
    
    for process in processes:
        process.wait()
        if process.returncode == 0:
            print("Command succeeded\n")
        else:
            print("Command failed\n")

if __name__ == "__main__":
    try:
        run_commands()
    except KeyboardInterrupt:
        print("Process interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")