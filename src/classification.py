from collections import defaultdict

import data
from similarity import sim_C_NCD_single, get_tool_label


def get_classification_label(scheme: callable, tool_label: str):
    match scheme.__name__:
        case "classify_best_match":
            return f"{tool_label}_best_match"
        case "classify_highest_average":
            return f"{tool_label}_highest_average"
        case "classify_KNN":
            return f"{tool_label}_KNN"
        case _:
            print("Unknown scheme: " + scheme.__name__)
            return f"{tool_label}_KNN"  # TODO: Fix KNN is currently passed as a lambda

def classify_files(scheme: callable, compressors: list[callable]):    
    for comp in compressors:
        label = get_classification_label(scheme, get_tool_label("NCD", comp))
        for file in data.validation_files:
            classification = scheme(file, lambda f, sf: sim_C_NCD_single(f, sf, comp))
            # print(f"File: {file.name}, Actual group: {file.group}, Classification: {classification}")
            data.classification_per_group_per_tool[label][file.group][classification] += 1            


def classify_best_match(file, sim_c):
    """
    Classify the classification files based on the best similarity match from the training files.
    Returns the group of the training file with the highest similarity score.
    """        
    best_match_score = -1
    best_match_group = -1
    
    # Get similarity score between the classification file and all training files.
    # Find the training file with the highest similarity score.
    for training_file in data.training_files:
        sim = sim_c(file, training_file)
        if sim > best_match_score:
            best_match_score = sim
            best_match_group = training_file.group
    
    return best_match_group


def classify_highest_average(file, sim_c):
    """
    Classify the classification files based on the highest average similarity score with the training files.
    Returns the group of the training file with the highest similarity score.
    """
    group_scores = defaultdict(float)
    
    # Calculate the average similarity score for each group
    for training_file in data.training_files:
        sim = sim_c(file, training_file)
        group_scores[training_file.group] += sim
    
    # Find the group with the highest average similarity score
    best_group = max(group_scores.items(), key=lambda x: x[1])[0]  # We use max to find the highest accumulated score which has the same effect as average since we have the same number of files in each group.
    
    return best_group


def classify_KNN(file, sim_c, k=5):
    similarities = []
    for training_file in data.training_files:
        similarities.append((sim_c(file, training_file), training_file))
    similarities.sort(key=lambda x: x[0])  # Sort by similarity score
    
    # Get the k files with the highest similarity scores
    k_nearest: list[tuple[float, data.File]] = similarities[-k:]  
    
    # Return the group of the most common file among the k nearest neighbors    
    group_counts = defaultdict(int)
    for _, training_file in k_nearest:
        group_counts[training_file.group] += 1
    best_group = max(group_counts.items(), key=lambda x: x[1])[0]
    return best_group