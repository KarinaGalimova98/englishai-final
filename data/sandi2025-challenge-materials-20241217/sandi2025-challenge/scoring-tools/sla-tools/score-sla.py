'''
Score individual set of predictions for SLA
Get the evaluation statistics of the predictions on a test set.

Copyright: S&I Challenge 2024
'''
import argparse
from scipy.stats import pearsonr, spearmanr, kendalltau, norm
from calibrate import read_preds, write_preds
import torch
from pathlib import Path
from path import makeDir, checkDirExists, checkFileExists, makeCmdPath

def calculate_mse(x1, x2):
    return torch.mean((x1 - x2) ** 2)

def calculate_rmse(x1, x2):
    return torch.sqrt(torch.mean((x1 - x2) ** 2))

def get_stats(preds, refs):
    '''
    This function returns the RMSE, PCC, SRC and KRC of a single set of reference scores and predictions.
    It assumes the input scores are out of 6 so scales them up below.
    '''
    rmse = calculate_rmse(torch.tensor(refs), torch.tensor(preds))
    pcc = pearsonr(refs, preds)[0]
    src = spearmanr(refs, preds)[0]
    krc = kendalltau(refs, preds)[0]
    return rmse, pcc, src, krc

def calculate_less_0105(y_pred, y):
    size = len(y)
    total05 = 0
    total1 = 0
    for a,b in zip(y, y_pred):
        diff = abs(a-b)
        if diff < 1:
            total1 += 1
        if diff < 0.5:
            total05 += 1
    less1 = 100.0*(total1/size)
    less05 = 100.0*(total05/size)
    return (less05, less1)

def calculate_less1(y_pred, y):
    less05, less1 = calculate_less_0105(y_pred, y)
    return less1

def calculate_less05(y_pred, y):
    less05, less1 = calculate_less_0105(y_pred, y)
    return less05

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate the statistics for the predictions on a test set.")
    parser.add_argument("--pred", type=str, required=True, help="Path to the prediction file for the test set.")
    parser.add_argument("--ref", type=str, required=True, help="Path to the reference scores for the test set.")
    args = parser.parse_args()

    checkFileExists(args.pred)
    checkFileExists(args.ref)
    
    # save command line arguments to file
    src_dir = str(Path(args.pred).parent)
    makeCmdPath (src_dir)

    # Read the predictions and reference
    ids, preds = read_preds(args.pred)
    ids_, refs = read_preds(args.ref)
    assert ids == ids_, "The submission ids in the prediction file do not match the reference file."

    # Calculate the statistics
    rmse, pcc, src, krc = get_stats(preds, refs)
    less05, less1 = calculate_less_0105(preds, refs)
    print("Infile {}:\nRMSE: {:.3f}, PCC: {:.3f}, SRC: {:.3f}, KRC: {:.3f}, LESS05: {:.1f}%, LESS1: {:.1f}%".format(args.pred, rmse, pcc, src, krc, less05, less1))
