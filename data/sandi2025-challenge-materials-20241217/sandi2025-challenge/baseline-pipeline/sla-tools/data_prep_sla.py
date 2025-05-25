#!/usr/bin/python3
# Prepare the data in tensor format, the main function is get_data()
import torch
import torch.nn as nn
from transformers import BertTokenizer

def get_submission_to_utt(responses_file, part):
    # Read the CTM file
    with open(responses_file, 'r') as f:
        lines = f.readlines()
    lines = [line.rstrip('\n') for line in lines]
    
    # Concatenate utterances for a speaker
    submission_to_utt = {}
    for line in lines:
        parts = line.split()
        if len(parts) < 5 or len(parts) > 6:
            continue  # Skip malformed lines

        submission_line = parts[0]  # First column (e.g., SI114J-00043-P10003)
        word = parts[4]  # Word column
        submission_part = int(submission_line[14])  # Extract the part from the submission ID

        if submission_part != part:
            continue  
        submissionid = submission_line[:12]  # Extract the submission ID (e.g., SI114J-00043)

        # Concatenate utterances for a submission test
        if submissionid not in submission_to_utt:
            submission_to_utt[submissionid] = word
        else:
            submission_to_utt[submissionid] = submission_to_utt[submissionid] + ' ' + word

    return submission_to_utt

def tokenize_text(utts, model='bert-base-uncased'):
    tokenizer = BertTokenizer.from_pretrained(model)
    encoded_inputs = tokenizer(utts, padding=True, truncation=True, return_tensors="pt")
    ids = encoded_inputs['input_ids']
    mask = encoded_inputs['attention_mask']
    return ids, mask

def get_data(responses_file, part=1):
    submission_to_utt = get_submission_to_utt(responses_file, part)
    submission_ids, utts = list(submission_to_utt.keys()), list(submission_to_utt.values())
    input_ids, mask = tokenize_text(utts, model='bert-base-uncased')
    return input_ids, mask, submission_ids

