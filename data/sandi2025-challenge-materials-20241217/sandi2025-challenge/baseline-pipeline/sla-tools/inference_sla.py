#!/usr/bin/python3
# Inference stage, get the predictions of the models on the test set.
import argparse
import csv
import os
import torch
from torch.utils.data import TensorDataset, DataLoader
from data_prep_sla import get_data
from models import BERTGrader
from pathlib import Path
from path import makeDir, checkDirExists, checkFileExists, makeCmdPath

def get_default_device():
    if torch.cuda.is_available():
        print("Got CUDA!")
        return torch.device('cuda')
    else:
        print("No CUDA found")
        return torch.device('cpu')

def inference(val_loader, model, device):
    preds = []

    # Switch to eval mode
    model.eval()

    with torch.no_grad():
        for i, (id, mask, ) in enumerate(val_loader):
            id = id.to(device)
            mask = mask.to(device)
            # Forward pass
            pred = model(id, mask)
            # Store
            preds += pred.tolist()
    return preds

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inference stage, get the predictions of a model on the test set")
    parser.add_argument("--model", type=str, required=True, help="Path to the trained model.")
    parser.add_argument("--ctm_file", type=str, required=True, help="CTM file with text responses to run ifnerence on.")
    parser.add_argument("--output_file", type=str, required=True, help="Output file for predictions.")
    parser.add_argument("--batch_size", type=int, default=8, help="Batch size for inference.")
    parser.add_argument("--part", type=int, default=4, help="Specify test part.")
    args = parser.parse_args()

    checkFileExists(args.model)
    checkFileExists(args.ctm_file)
    output_dir = str(Path(args.output_file).parent)
    makeDir ( output_dir, False )            
    
    # save command line arguments to file
    makeCmdPath (output_dir)
    
    # Get the device
    device = get_default_device()

    # Load the data
    input_ids, mask, submission_ids = get_data(args.ctm_file, part=args.part)
    print('size of data: ', len(input_ids))
    test_ds = TensorDataset(input_ids, mask)
    test_dl = DataLoader(test_ds, batch_size=args.batch_size)

    # Load the model
    model = BERTGrader()
    model.load_state_dict(torch.load(args.model))
    model.to(device)

    # Get the predictions
    preds = inference(test_dl, model, device)

    # Save the predictions
    with open(args.output_file, 'w') as f:
        tsv_writer = csv.writer(f, delimiter='\t', lineterminator='\n')
        for submission, pred in zip(submission_ids, preds):
            tsv_writer.writerow([submission, pred])
    print(f"Predictions saved to {args.output_file}")
