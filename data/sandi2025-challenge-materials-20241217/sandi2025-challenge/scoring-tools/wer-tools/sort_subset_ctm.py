'''
sort and extract subset of files from CTM to match STM
- remove phrase markers "_PH##" if exist in file names

Copyright: S&I Challenge 2024
'''
import os
import argparse
import sys
from pathlib import Path
from path import makeDir, checkDirExists, checkFileExists, makeCmd, makeCmdPath

def read_ctm ( ctm_fname ):
    ctm_info = {}
    fileids = []
    for line in open (ctm_fname):
        if line.strip():
            lineitems = line.strip().split()
            fileid = lineitems[0].split('_PH')[0]
            if fileid not in ctm_info:
                ctm_info[fileid] = []
                fileids.append(fileid)
            ctmstg = (' '.join(lineitems[1:]))
            ctm_info[fileid].append(ctmstg)
    return fileids, ctm_info

def get_stm_fileids ( stm_fname ):
    fileids = []
    for line in open (stm_fname):
        if line.strip():
            lineitems = line.strip().split()
            if ";;" in lineitems[0]:
                # ignore comment lines
                continue
            fileid = lineitems[0].split('_PH')[0]
            if fileid not in fileids:
                fileids.append(fileid)
    return fileids

def main (args):
    #------------------------------------------------------------------------------
    # read in command line arguments
    #------------------------------------------------------------------------------
    input_ctm = args.input_ctm
    input_stm = args.input_stm
    output_ctm = args.output_ctm

    checkFileExists ( input_ctm )
    checkFileExists ( input_stm )
    output_dir = str(Path(output_ctm).parent)
    makeDir ( output_dir, False )        
     
    #------------------------------------------------------------------------------
    # save command line arguments to file
    #------------------------------------------------------------------------------
    makeCmdPath (output_dir)

    #------------------------------------------------------------------------------
    # read in CTM and write out sorted info
    #------------------------------------------------------------------------------
    fileids, ctm_info = read_ctm (input_ctm)
    sel_fileids = get_stm_fileids (input_stm)
    sel_fileids = sorted(sel_fileids)
    fp = open(output_ctm, 'w')
    for fileid in sel_fileids:
        for line in ctm_info[fileid]:
            print('%s %s' % (fileid, line), file=fp)
    fp.close()


if __name__ == "__main__":
    #------------------------------------------------------------------------------
    # arguments
    #------------------------------------------------------------------------------
    parser = argparse.ArgumentParser(description="Extract and sort (possible) subset of files from CTM")
    parser.add_argument('--input_ctm', required=True, help="Path to the input CTM file")
    parser.add_argument('--input_stm', required=True, help="Path to the STM file")
    parser.add_argument('--output_ctm', required=True, help="Path to the output CTM file")

    args = parser.parse_args()
    main(args)
