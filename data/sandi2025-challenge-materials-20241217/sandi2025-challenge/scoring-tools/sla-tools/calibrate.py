'''
Calibrate the predictions based on the factors estimated from a calibration set.

Copyright: S&I Challenge 2024
'''
import os
import argparse
from statistics import mean
import numpy as np
import csv
from pathlib import Path
from path import makeDir, checkDirExists, checkFileExists, makeCmdPath

def read_preds(pred_file):
    """Read the predictions from a tsv file."""
    ids, preds = [], []
    with open(pred_file, 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            id, pred = line.strip().split('\t')
            pred = float(pred)
            preds.append(pred)
            ids.append(id)
    return ids, preds

def write_preds(pred_file, ids, preds):
    """Write the predictions to a tsv file."""
    with open(pred_file, 'w') as f:
        tsv_writer = csv.writer(f, delimiter='\t', lineterminator='\n')
        for id, pred in zip(ids, preds):
            tsv_writer.writerow([id, pred])
    print(f"Predictions saved to {pred_file}")
    return

def best_fit_slope_and_intercept(xs,ys):
    """Estimate the calibration factor for a set of predictions."""
    xs = np.array(xs)
    ys = np.array(ys)
    m = (((mean(xs)*mean(ys)) - mean(xs*ys)) /
         ((mean(xs)*mean(xs)) - mean(xs*xs)))

    b = mean(ys) - m*mean(xs)

    return m, b

def apply_calibration(preds, m, b):
    """Apply the calibration factor to a set of predictions."""
    return [m*x + b for x in preds]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calibrate the predictions based on the factors estimated from a calibration set.")
    parser.add_argument("--pred", type=str, required=True, help="Path to the prediction file for the test set.")
    parser.add_argument("--ref", type=str, required=True, help="Path to the reference file for the test set.")
    parser.add_argument("--calib_coeffs", type=str, required=True, help="Calibration coefficients file (apply if exists else compute and apply).")
    args = parser.parse_args()

    checkFileExists(args.pred)
    checkFileExists(args.ref)
    calib_coeffs_file = args.calib_coeffs
    compute_calib = True
    if os.path.exists(calib_coeffs_file) is True:
        compute_calib = False
    else:
        calib_dir = str(Path(calib_coeffs_file).parent)
        makeDir(calib_dir, False)

    pred_dir = str(Path(args.pred).parent)
    makeCmdPath(pred_dir)

    # Read the predictions and reference
    ids, preds = read_preds(args.pred)
    ids_, refs = read_preds(args.ref)
    assert ids == ids_, "The submission ids in the prediction file do not match the reference file."
    
    # Estimate calibration factors
    if compute_calib:
        m, b = best_fit_slope_and_intercept(preds, refs)
        fp = open(calib_coeffs_file, 'w')
        tsv_writer = csv.writer(fp, delimiter='\t', lineterminator='\n')
        tsv_writer.writerow([m, b])
        print(f"Calibration coefficients saved to {calib_coeffs_file}")        
    else:
        for line in open(calib_coeffs_file, 'r'):
            if line.strip():
                m, b = line.strip().split()
                m = float(m)
                b = float(b)
                
    print("Calibration factor m:", m)
    print("Calibration factor b:", b)
    cali_preds = apply_calibration(preds, m, b)

    # Write to the output
    calibrated_preds_file = args.pred.replace('.tsv', '_calibrated.tsv')
    write_preds(calibrated_preds_file, ids, cali_preds)
    
