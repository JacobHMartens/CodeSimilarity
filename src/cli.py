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
                raise ValueError(f"Unknown compressor: {value}")
        setattr(namespace, self.dest, compressors)


def parse_args():
    parser = argparse.ArgumentParser()
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
                    argparse.ArgumentError(f"K in knnK must be an integer between 1 and 300. Got {k}.")
            else:
                argparse.ArgumentError(f"Invalid classification scheme: {scheme}. Must be one of ['bm', 'ha', 'knnK'], where K is an integer, 0 < K <= 300.")
        setattr(namespace, self.dest, schemes)
    parser.add_argument("num_dirs", 
                        type=int, 
                        help="Number of directories to process from the dataset.")
    parser.add_argument("num_files", 
                        type=int, 
                        help="Number of files to process in each directory.")
    parser.add_argument("-C", "--compressors", 
                        type=str, 
                        nargs="+", 
                        choices=["bzip2", "gzip", "zlib", "zstandard", "zstd"], 
                        default="bzip2", 
                        action=CompFuncAction)
    parser.add_argument("-cf", "--num-classification-files",
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
    parser.add_argument("-PH", "--PLOT_HEATMAP", 
                        action="store_true", 
                        help="Generate heatmaps of the similarity matrices.")
    parser.add_argument("-PF", "--PLOT_FSCORES", 
                        action="store_true", 
                        help="Plot F-scores for the tools.")
    parser.add_argument("-NO-CL", "--NO_CLUSTER",
                        action="store_true", 
                        help="Disable clustering of the similarity matrices.")
    
    args = parser.parse_args()
    required_flags = ["-NCD", "-ICD"]
    if not (args.ICD or args.NCD):
        parser.error(f"At least one of the following flags must be set: {required_flags}")
    
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
            
    if not args.NO_CLUSTER:
        for sim_id, sim_matrix in data.sim_matrices.items():
            print("clusting", sim_id)
            data.sim_matrices[sim_id] = data.cluster_matrices_by_groups(sim_matrix)

    if args.PLOT_HEATMAP:
        show_plots = True
        plots.create_heatmap_plots()
            
    if args.PLOT_FSCORES:
        show_plots = True    
        plots.create_fscores_plot()
        
    if args.classify > 0:
        data.load_classification_data(args.num_classification_files)
        for scheme in args.schemes:
            classify_files(scheme, args.compressors)

    if show_plots:
        plots.show_plots()