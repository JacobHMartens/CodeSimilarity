import argparse
import data
import plots
from similarity import get_tool_label, sim_C_ICD, sim_C_NCD
from classification import classify_best_match, classify_files, classify_highest_average, classify_KNN
import tools.compressors as comp


class CompFuncAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        compressors = []
        for value in values:
            if hasattr(comp, f"comp_{value}"):
                compressors.append(getattr(comp, f"comp_{value}"))
            else:
                raise argparse.ArgumentError(self, f"Unknown compressor: {value}")
        setattr(namespace, self.dest, compressors)


class SchemeAction(argparse.Action):
    def __call__(self, parser, namespace, values: list[str], option_string=None):
        schemes = []
        for scheme in values:
            if scheme == "bm":
                schemes.append(classify_best_match)
            elif scheme == "ha":
                schemes.append(classify_highest_average)
            elif scheme.startswith("knn") and scheme[3:].isdigit():
                k = int(scheme[3:])
                if 0 < k <= 300:
                    schemes.append(lambda file, sim_c: classify_KNN(file, sim_c, k))
                else:
                    raise argparse.ArgumentError(self, f"K in knnK must be an integer between 1 and 300. Got {k}.")
            else:
                raise argparse.ArgumentError(self, f"Invalid classification scheme: {scheme}. Must be one of ['bm', 'ha', 'knnK'], where K is an integer, 0 < K <= 300.")
        setattr(namespace, self.dest, schemes)


def parse_args(args: str=None):
    parser = argparse.ArgumentParser(exit_on_error=False)
    
    # POSITIONAL ARGUMENTS
    parser.add_argument("num_dirs", 
                        type=int, 
                        help="Number of directories to process from the dataset. 0 < num_dirs <= 250.")
    parser.add_argument("num_files", 
                        type=int, 
                        help="Number of files to process in each directory. 0 < num_files <= 300.")
    
    # OPTIONS
    parser.add_argument("-c", "--compressors", 
                        type=str, 
                        nargs="+", 
                        choices=["bzip2", "gzip", "zlib", "zstandard", "zstd"], 
                        required=True, 
                        action=CompFuncAction)
    parser.add_argument("-ncf", "--num-classification-files",
                        type=int,
                        metavar="{1-300}",
                        choices=range(1, 301),
                        default=10, 
                        help="Number of files to use for classification, where 0 < num_files <= 300. Default is 10 files.\
                              The selected number of files will as much as possible be different from the sample files used for the similarity calculation.")
    parser.add_argument("-cs", "--schemes", "--classification-schemes",
                        type=str,
                        nargs="+",
                        metavar={"bm", "ha", "knn{1-300}"},
                        choices=["bm", "ha"] + [f"knn{i}" for i in range(1, 301)],
                        default=[classify_best_match],
                        action=SchemeAction,
                        help="Classification schemes to use for the classification of files. Choose one or more classification schemes from {'bm', 'knn[1-300]', 'ha'}.\
                              Where 'bm' is 'Best Match', 'knn[1-300]' is 'K-Nearest Neighbors' with 1 <= K <= 300 files, and 'ha' is 'highest average'.\
                              Default is 'bm knn10 ha'.")
    
    # FLAGS
    parser.add_argument("-NCD", 
                        action="store_true", 
                        help="Use Normalized Compression Distance (NCD) for similarity calculation.")
    parser.add_argument("-ICD", 
                        action="store_true", 
                        help="Use Inclusion Compression Divergence (ICD) for similarity calculation.")
    parser.add_argument("-PH", "--plot-heatmaps", 
                        action="store_true", 
                        help="Generate heatmaps of the similarity matrices.")
    parser.add_argument("-PF", "--plot-fscores", 
                        action="store_true", 
                        help="Plot F-scores for the tools.")
    parser.add_argument("-PC", "--plot-classification", 
                        action="store_true", 
                        help="Plot classification results.")
    parser.add_argument("-CL", "--cluster",
                        action=argparse.BooleanOptionalAction, 
                        default=True,
                        help="Enable clustering of the similarity matrices (default). Disable with --no-cluster.")
    parser.add_argument("-CLFY", "--classify",
                        action="store_true",
                        help="Classify the classification-files using the selected classification schemes.")
    parser.add_argument("-I", "--interactive",
                        action="store_true", 
                        help="Run tool in interactive mode (keep CLI alive).")
    
    args = parser.parse_args(args)
    
    if not 0 < args.num_dirs <= 250:
        raise argparse.ArgumentError(None, f"Number of directories must be between 1 and 250. Got {args.num_dirs}.")
    if not 0 < args.num_files <= 300:
        raise argparse.ArgumentError(None, f"Number of files per directory must be between 1 and 300. Got {args.num_files}.")
        
    required_flags = ["-NCD", "-ICD"]
    if not (args.ICD or args.NCD):
        raise argparse.ArgumentError(None, f"At least one of the following flags must be set: {required_flags}")
    
    return args
    

def run():
    args = parse_args()
    data.load_java250_data(args.num_dirs, args.num_files)
        
    show_plots = False
    if args.NCD:
        for comp in args.compressors:
            sim_matrix = sim_C_NCD(data.sample_files, comp)
            data.sim_matrices[get_tool_label("NCD", comp)] = sim_matrix
    
    if args.ICD:
        for comp in args.compressors:
            sim_matrix = sim_C_ICD(data.sample_files, comp)
            data.sim_matrices[get_tool_label("ICD", comp)] = sim_matrix
            
    if args.cluster:
        for sim_id, sim_matrix in data.sim_matrices.items():
            data.sim_matrices[sim_id] = data.cluster_matrices_by_groups(sim_matrix)

    if args.plot_heatmaps:
        show_plots = True
        plots.create_heatmap_plots()
            
    if args.plot_fscores:
        show_plots = True    
        plots.create_fscores_plot()
        
    if args.classify > 0:
        data.load_classification_data(args.num_classification_files)
        for scheme in args.schemes:
            classify_files(scheme, args.compressors)
            print(data.classification_per_group_per_tool)
            
    if args.plot_classification:
        show_plots = True
        plots.create_classification_plot()

    if show_plots:
        plots.show_plots()
        
    if args.interactive:
        print("Interactive mode enabled. Press Ctrl+C to exit.")
        run_interactive()
        
            

def run_interactive():
    try:
        while True:
            args = input("Enter arguments: ").strip()
            parse_args(args.split())
            run_interactive()
    except KeyboardInterrupt:
        print("\nExiting interactive mode.")
    except argparse.ArgumentError as e:
        print(f"Error: {e}")
        run_interactive()
