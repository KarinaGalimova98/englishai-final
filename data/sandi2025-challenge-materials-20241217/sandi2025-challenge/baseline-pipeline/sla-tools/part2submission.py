#!/usr/bin/python3
# Input the per part predictions and average to get the holistic predictions.
import os
import argparse
from calibrate import write_preds
from pathlib import Path
from path import makeDir, checkDirExists, checkFileExists, makeCmdPath

def read_predictions(pred_file):
    """
    pred_file is a tsv file with the first column being the id and the second column being the prediction
    Return a dictionary with id as key and prediction as value.
    """
    preds = dict()
    with open(pred_file, 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            id, pred = line.strip().split('\t')
            pred = float(pred)
            preds[id] = pred
    return preds

def average_predictions(all_preds):
    """
    All_preds is a list of 4 predictions, each item in the list is a dictionary with id as key and prediction as value
    Return a dictionary with id as key and average prediction as value.
    """
    assert len(all_preds) == 4
    avg_preds = {}
    for id in all_preds[0].keys():
        avg_preds[id] = 0
        count = 0
        for i in range(4):
            if id in all_preds[i]:
                avg_preds[id] += all_preds[i][id]
                count += 1
        avg_preds[id] /= count
        if count != 4:
            print(f"Warning: ID {id} not found in all predictions!")
            
    return avg_preds

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Average the predictions for the four parts to get the submission predictions.")
    parser.add_argument("--input", type=str, required=True, help="Path to each per-part predictions, separated by space.")
    parser.add_argument("--output", type=str, help="Path to the overall submission predictions.")
    args = parser.parse_args()

    pred_files = args.input.split()
    for pred_file in pred_files:
        checkFileExists(pred_file)
    output_file = args.output
    output_dir = str(Path(output_file).parent)
    makeDir(output_dir, False)
    
    # Save the command run
    makeCmdPath(output_dir)

    # Read the predictions
    all_preds = []
    for pred_file in pred_files:
        preds = read_predictions(pred_file)
        all_preds.append(preds)
    
    # Average the predictions to get holistic predictions
    avg_preds = average_predictions(all_preds)
    ids = sorted(avg_preds.keys())
    preds = [avg_preds[id] for id in ids]

    # Write the holistic predictions
    write_preds(args.output, ids, preds)
