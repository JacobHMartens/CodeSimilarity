import argparse
import data
import plots
from similarity import get_tool_label, sim_C_ICD, sim_C_NCD
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
            sim_matrix = sim_C_NCD(data.files, comp)
            data.sim_matrices[get_tool_label("NCD", comp)] = sim_matrix
    
    if args.ICD:
        for comp in args.compressors:
            sim_matrix = sim_C_ICD(data.files, comp)
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

    if show_plots:
        plots.show_plots()