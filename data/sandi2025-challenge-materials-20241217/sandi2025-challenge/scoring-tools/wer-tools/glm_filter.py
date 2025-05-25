'''
appy GLM filtering to CTM and STM

Copyright: S&I Challenge 2024
'''
import subprocess
import argparse
import os
import sys
from path import checkDirExists, checkFileExists, makeCmdPath


def run_perl_script(glm, stm, ctm):
    perl_script_args = ['-h', 'rt-stt', '-l', 'english', '-g', glm, '-r', stm, '-k', ctm]

    try:
        subprocess.run(['perl', './scoring-tools/wer-tools/hubscr07.sort.filt.pl'] + perl_script_args, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing Perl script: {e}")

def main():
    parser = argparse.ArgumentParser(description="Run Perl script with specified arguments")
    parser.add_argument('--glm', required=True, help="Path to the GLM file")
    parser.add_argument('--stm', required=True, help="Path to the STM file")
    parser.add_argument('--ctm', required=True, help="Path to the CTM file")

    args = parser.parse_args()

    checkFileExists(args.glm)
    checkFileExists(args.ctm)
    checkFileExists(args.stm)
    makeCmdPath (args.ctm)

    run_perl_script(args.glm, args.stm, args.ctm)    

if __name__ == "__main__":
    main()
