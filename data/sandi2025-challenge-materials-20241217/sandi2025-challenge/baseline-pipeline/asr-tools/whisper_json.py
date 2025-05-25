'''
Functions for extracting info from Whisper JSON files

Copyright: S&I Challenge 2024
'''
import os
import json
import argparse
import sys
import re
import string
from pathlib import Path
from path import makeDir, checkDirExists, checkFileExists, makeCmdPath

def combine_words(words): 
    '''
    Combine words based on the specified rules:
    - If a word does not have a space before it, combine it with the previous word.
    - Do not combine if the previous word ends with a punctuation mark.
    - Do not combine if the current word begins with a punctuation mark.
    '''
    combined_words = []
    i = 0

    while i < len(words):
        current_word = words[i]['word']

        # Check if the current word can be combined with the previous one
        if (
            i > 0  # Not the first word
            and not words[i-1]['word'].endswith(' ')  # Previous word has no trailing space
            and not current_word.startswith(' ')  # Current word has no leading space
            and not words[i-1]['word'].endswith(('.', ',', '!', '?', ':', ';'))  # Previous word doesn't end with punctuation
            and not current_word.startswith(('.', '!', '?', ':', ';'))  # Current word doesn't start with punctuation
            # if start with comma, combine with the previous word, e.g. "100" ",000" -> "100,000"
        ):
            # Combine the current word with the previous one
            combined_word = combined_words[-1]['word'] + current_word
            combined_word_dict = {
                'word': combined_word,
                'start': combined_words[-1]['start'],
                'end': words[i]['end'],
                'probability': (combined_words[-1]['probability'] + words[i]['probability']) / 2
            }

            # Replace the last combined word with the new combined word
            combined_words[-1] = combined_word_dict
        else:
            # Add the current word as is to the combined list
            combined_words.append(words[i])

        i += 1

    return combined_words

def split_words(words):  #add other punc, split after punc (punc belongs to the left word)
    # split the word if it contains punctuation (i.e. xxx...xxx, (ellipsis)) in the
    # middle(must between letters); e.g. you...I -> you... I
    # probability: same for the split words
    # time: divided equally among the split words
    split_words = []
    pattern = re.compile(r'([a-zA-Z]+)(\.{3,})([a-zA-Z]+)')

    for word in words:
        word_text = word['word'].strip()
        match = pattern.search(word_text)
        
        if match:
            # Ensure ellipsis is between alphabetic sequences and not followed by punctuation
            ellipsis_index = word_text.find(match.group(2))
            if ellipsis_index + len(match.group(2)) < len(word_text) and word_text[ellipsis_index + len(match.group(2))] not in string.punctuation:
                # print(word)
                split_word = word_text.split(match.group(2))
                start = word['start']
                end = word['end']
                probability = word['probability']
                wlen = (end - start) / len(split_word)
                for i, part in enumerate(split_word):
                    # if i == 0 and word_text.startswith("..."): # Keep the ... for the first word
                    #     part = "..." + part
                    # if i == len(split_word) - 1 and word_text.endswith("..."): # Keep the ... for the last word
                    #     part += "..."
                    if i < len(split_word) - 1: # Keep the ... for the previous word, but not for the next word
                        part += "..."
                    split_word_dict = {
                        'word': part,
                        'start': start,
                        'end': start + wlen,
                        'probability': probability
                    }
                    split_words.append(split_word_dict)
                    start += wlen
            else:
                continue
        else:
            split_words.append(word)

    return split_words

def json_to_ctm_lines (json_dir):
    ctm_lines = []

    for json_file in os.listdir(json_dir):
        if json_file.endswith(".json"):
            json_path = os.path.join(json_dir, json_file)
            json_name = json_file.split(".")[0]
            try:
                with open(json_path, 'r') as file:
                    text = json.load(file)

                    for seg in text.get("segments", []):
                        modified_words_list = []

                        for word in seg.get("words", []):
                            start = word.get("start", 0.0)
                            end = word.get("end", 0.0)
                            word_text = word.get("word", "")  
                            probability = word.get("probability", 1.0)

                            modified_word_dict = {'word': word_text, 'start': start,
                                                  'end': end, 'probability': probability}
                            modified_words_list.append(modified_word_dict)

                        # Combine words without empty space before
                        modified_words_list = combine_words(modified_words_list)
                        modified_words_list = split_words(modified_words_list)
                        # get each word in the modified_words_list and do the
                        # normalization and write to ctm file
                        for w in modified_words_list:
                            word_text = w['word'].strip()
                            start = w['start']
                            end = w['end']
                            probability = w['probability']

                            if word_text:
                                start = float(w['start'])
                                wlen = (float(w['end']) - float(w['start'])) / len(word_text.split())
                                for i in word_text.split():
                                    ctm_line = f"{json_name} 1 {start:.2f} {wlen:.2f} {i} {probability:.2f}"
                                    ctm_lines.append(ctm_line)
                                    start += wlen

            except Exception as e:  
                print(f"Error processing {json_path}: {str(e)}")
    return ctm_lines

