'''
    This script is to be used to perform evaluation (for feedback) for spoken GEC systems.

    Inputs:
        (a) Manual ASR transcription (reference transcription)
        (b) Hypothesis ASR transcription (generated by ASR system)
        (c) Reference GEC text
        (d) Hypothesis GEC text
    
    THIS SCRIPTS ASSUMES THAT ALL PASSED FILES ARE ALREADY ALIGNED (a new sentence per line)
    
    Score:
        (1) Compute errant edits from (a) to (c) = reference edits
        (2) Compute errant edits from (b) to (d) = hypothesis edits
        (3) Compute precision, recall, F0.5 - requiring edits to match, in edit change specificed (by Errant) and the position in the source document.
                     The position is adjusted to account for ASR errors causing differences between source documents (a) and (b)


    How is this distinct from standard textual ERRANT?
        Errant by default computes 'span-based' F0.5 score.
        This requires the hypothesis edit and reference edit to be in the same position in the source document.
        However, in spoken GEC the source document is not the same for hypothesis and reference edits,
        as ASR errors can create a misalignment between (a) and (b). This means for spoken GEC many edits are unfairly labeled as false positives.
        Hence, in this tool we check for ASR errors that cause misalignment and then we align.

    Credit:
        The need for spoken GEC evaluation was raised by **Thomas Hardman**.
        This script is based on his code for spoken GEC evaluation.
        The code has been enhanced to offer a more granular breakdown by edit-type with the flag --split_edit_type
'''

import errant
import numpy as np
import Levenshtein
import argparse
from tqdm import tqdm
from collections import defaultdict

def get_file_data(fname):
    with open(fname, 'r') as f:
        data = f.readlines()
    data = [d.strip('\n') for d in data]
    return data

def core_args():
    commandLineParser = argparse.ArgumentParser(allow_abbrev=False)
    commandLineParser.add_argument('--ref_asr', type=str, required=True, help='filepath for manual ASR transcript')
    commandLineParser.add_argument('--hyp_asr', type=str, required=True, help='filepath for hypothesis ASR transcript')
    commandLineParser.add_argument('--ref_gec', type=str, required=True, help='filepath for reference GEC text')
    commandLineParser.add_argument('--hyp_gec', type=str, required=True, help='filepath for hypothesis GEC text')
    commandLineParser.add_argument('--split_edit_type', action='store_true', help='Breakdown scores by edit type')

    return commandLineParser.parse_known_args()

def get_stc_edits(annotator, src, tgt):
    src = annotator.parse(src)
    tgt = annotator.parse(tgt)
    edits = annotator.annotate(src, tgt)
    return edits

def equal_edits(edit_hyp, edit_ref, asr_shifts):
    if all([edit_hyp.o_start + asr_shifts[0][edit_hyp.o_start] == edit_ref.o_start,
            edit_hyp.o_end + asr_shifts[1][edit_hyp.o_end] == edit_ref.o_end,
            edit_hyp.c_str == edit_ref.c_str,
            edit_hyp.o_str == edit_ref.o_str]):
        return True
    return False



def errant_spoken(source_asr_stcs_al, pred_stcs_al, target_stcs_al, source_trans_stcs_al):
    '''
        Calculates TP, FP, FN for evaluating spoken GEC per edit type.
        source_asr_stcs_al - list of aligned ASR output sentences (b)
        pred_stcs_al - list of aligned predicted sentences (d)
        target_stcs_al - list of aligned reference sentences (c)
        source_trans_stcs_al - list of aligned manually transcribed sentences (a)
    '''
    tp = defaultdict(int)
    fp = defaultdict(int)
    ref_tot = defaultdict(int)

    annotator = errant.load('en')

    for stc_asr, stc_pred, stc_tgt, stc_trans in tqdm(zip(source_asr_stcs_al, pred_stcs_al, target_stcs_al, source_trans_stcs_al), total=len(source_asr_stcs_al)):
        hyp_edits = get_stc_edits(annotator, stc_asr, stc_pred)
        ref_edits = get_stc_edits(annotator, stc_trans, stc_tgt)

        # update total number of reference edits per edit type
        for ref_edit in ref_edits:
            ref_tot[ref_edit.type] += 1

        # find operations to get from transcription to asr
        asr_editops = Levenshtein.opcodes(stc_asr.split(' '), stc_trans.split(' '))

        # initialise array to store required span shifts for asr stc - top row stores shift required for start of span
        # bottom row stores shift required for end of span
        asr_shifts = np.zeros((2, len(stc_asr.split(' ')) + 1))

        for opcode, asr_start, asr_stop, trans_start, trans_stop in asr_editops:
            if opcode == 'insert':
                try:
                    asr_shifts[0, asr_start] += trans_stop - trans_start  # start of edits beginning on/after insertion shifted right by length of inserted seq
                    asr_shifts[1, asr_start+1] += trans_stop - trans_start # end spans only shifted right after insertion, not on
                except:
                    #print('one failed attempt at accounting for insert error.')
                    continue
            elif opcode == 'delete':
                asr_shifts[:, asr_stop] += -(asr_stop - asr_start)

        asr_shifts = np.cumsum(np.array(asr_shifts), axis=1)

        # compare edits in sentence
        for hyp_edit in hyp_edits:
            correct = False
            for ref_edit in ref_edits:
                if equal_edits(hyp_edit, ref_edit, asr_shifts):
                    tp[ref_edit.type] += 1
                    correct = True
                    break
            if not correct:
                fp[hyp_edit.type] += 1

    fn = {k:ref_tot[k] - tp[k] for k in ref_tot}
    fn = defaultdict(int, fn)
    return tp, fp, fn


def compute_p_r_f05(tp_val, fp_val, fn_val):
    p = tp_val/(tp_val + fp_val)
    r = tp_val/(tp_val + fn_val)
    f_05 = 1.25 * (p * r) / (0.25 * p + r)
    return p, r, f_05

def print_results(tp, fp, fn, split_edit_type=False):
    '''
        Computes the precision, recall and F0.5 scores (per edit type if specified)
    '''
    if split_edit_type:
        edit_types = list(set(tp.keys()) | set(fp.keys()) | set(fn.keys()))
        for edit_type in edit_types:
            try:
                p, r, f_05 = compute_p_r_f05(tp[edit_type], fp[edit_type], fn[edit_type])
                print()
                print(f'Edit Type:\t{edit_type}')
                print(f'P:\tR:\tF0.5')
                print(f'%.3f\t%.3f\t%.3f' % (p, r, f_05))
            except:
                continue
        print(f'\n')
    p, r, f_05 = compute_p_r_f05(sum(tp.values()), sum(fp.values()), sum(fn.values()))
    print(f'Overall results:')
    print(f'P:\tR:\tF0.5')
    print(f'%.3f\t%.3f\t%.3f' % (p, r, f_05))
    

if __name__ == '__main__':

    # load input files
    args, c = core_args()

    # calculate spoken GEC feedback metrics per edit type
    tp, fp, fn = errant_spoken(get_file_data(args.hyp_asr), get_file_data(args.hyp_gec), \
                               get_file_data(args.ref_gec), get_file_data(args.ref_asr))
    print_results(tp, fp, fn, split_edit_type=args.split_edit_type)
