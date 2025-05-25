'''
Convert Whisper json file to CTM format - requires timestamps

Copyright: S&I Challenge 2024
'''
import os
import json
import argparse
import sys
import re
import string
from pathlib import Path
from whisper_json import combine_words, split_words, json_to_ctm_lines
from path import makeDir, checkDirExists, checkFileExists, makeCmdPath

def convert_json_to_ctm (json_dir_list, output_ctm):
    ctm_lines = []
    
    for json_dir in json_dir_list:
        ctm_lines = ctm_lines + json_to_ctm_lines ( json_dir )

    # Sort ctm_lines based on the filename
    ctm_lines.sort(key=lambda x: x.split()[0])

    with open(output_ctm, 'w') as ctm_out:
        for line in ctm_lines:
            print(line, file=ctm_out)

def main():
    parser = argparse.ArgumentParser(description="Convert JSON files to CTM format")
    parser.add_argument('--json_dir', required=True, help="One or more directory containing JSON files")
    parser.add_argument('--output_ctm', required=True, help="Output CTM file")
    args = parser.parse_args()

    # file/dir checks and set-up
    json_dir_list = args.json_dir.split(' ')
    for json_dir in json_dir_list:
        checkDirExists (args.json_dir)
    output_dir = str(Path(args.output_ctm).parent)
    makeDir ( output_dir, False )            

    # save command line arguments to file
    makeCmdPath (output_dir)

    # convert file format
    convert_json_to_ctm(json_dir_list, args.output_ctm)


if __name__ == "__main__":
    main()
