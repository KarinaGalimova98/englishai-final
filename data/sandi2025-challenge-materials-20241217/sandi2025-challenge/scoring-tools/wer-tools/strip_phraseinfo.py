'''
Strip phrase IDs from CTM for scoring

Copyright: S&I Challenge 2024
'''
import sys
import os
import argparse

from path import makeDir, checkDirExists, checkFileExists, makeCmdPath

def main ( args ):
    #------------------------------------------------------------------------------
    # read in command line arguments
    #------------------------------------------------------------------------------
    stm_fname = args.stm_fname
    tgt_fname = args.tgt_fname
    
    checkFileExists ( stm_fname)

    tgt_dir = os.path.dirname ( tgt_fname )
    if len(tgt_dir) > 0:
        makeDir ( tgt_dir, False )        

    #------------------------------------------------------------------------------
    # save command line arguments to file
    #------------------------------------------------------------------------------
    makeCmdPath (tgt_dir)
    
    #------------------------------------------------------------------------------
    # read in STM file
    #------------------------------------------------------------------------------
    fileids=[]
    fileinfo={}
    fp = open(stm_fname, 'r')
    fpm = open(tgt_fname, 'w')
    for line in fp:
        if line.strip():
            lineitems = line.strip().split()
            if ';;' in lineitems[0]:
                fpm.write('%s' % line)
                continue
            # split at phrase marker (if exists)
            fileid=lineitems[0].split('_PH')[0]
            if fileid not in fileinfo:
                fileids.append(fileid)
                fileinfo[fileid] = []
            fileinfo[fileid].append(line.strip())
    fp.close()

    for fileid in fileids:
        seg_st_time = 0.0
        seg_en_time = 0.0
        seg_stg = ''
        for line in fileinfo[fileid]:
            lineitems = line.split()
            ph_st_time = float(lineitems[3])
            ph_en_time = float(lineitems[4])
            if 'IGNORE_TIME' in line:
                if len(seg_stg) > 0:
                    fpm.write('%s %s %s %.2f %.2f %s %s\n' %
                              (fileid, lineitems[1], lineitems[2], seg_st_time, seg_en_time, lineitems[5], seg_stg))
                fpm.write('%s\n' % line)
                seg_stg=''
                seg_st_time = ph_en_time
                seg_en_time = ph_en_time
            else:
                seg_stg = seg_stg + ' ' + ' '.join(lineitems[6:])
                seg_en_time = ph_en_time
        if len(seg_stg) > 0:
            fpm.write('%s %s %s %.2f %.2f %s %s\n' %
                      (fileid, lineitems[1], lineitems[2], seg_st_time, seg_en_time, lineitems[5], seg_stg))

    fpm.close()

if __name__ == "__main__":
    #------------------------------------------------------------------------------
    # arguments
    #------------------------------------------------------------------------------
    commandLineParser = argparse.ArgumentParser (
        description = 'Merge continguous segments in STM')
    commandLineParser.add_argument ('stm_fname',
        metavar = 'stm_fname', type = str,
        help = 'STM file to be edited')
    commandLineParser.add_argument ('tgt_fname',
        metavar = 'tgt_fname', type = str,
        help = 'Target output STM file')

    args = commandLineParser.parse_args()
    main(args)

    
    
                
