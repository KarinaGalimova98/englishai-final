#! /usr/bin/python
'''
Run Whisper ASR transcription
'''
import argparse
import os
import json
import torch
from pathlib import Path
from path import makeDir, checkDirExists, checkFileExists, makeCmdPath
import sys

import whisper
import time
from tqdm import tqdm
from whisper_json import json_to_ctm_lines

def read_wav_list(infile):
    idlist = []
    wavlist = []
    with open(infile, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            fileid, wav = line.strip().split()
            idlist.append(fileid)
            wavlist.append(wav)
    return idlist, wavlist

def get_seg_lines_from_result(result, fileid):
    seg_lines = []
    for seg in result['segments']:
        seg_dict = dict()
        seg_dict['id'] = fileid
        seg_dict['start_time'] = seg['start']
        seg_dict['end_time'] = seg['end']
        seg_dict['text'] = seg['text']
        seg_dict['tokens'] = seg['tokens']
        seg_dict['temperature'] = seg['temperature']
        seg_dict['avg_logprob'] = seg['avg_logprob']
        seg_dict['compression_ratio'] = seg['compression_ratio']
        seg_dict['no_speech_prob'] = seg['no_speech_prob']
        seg_lines.append(seg_dict)
    return seg_lines

def get_seg_lines_from_nbest_result(result, fileid):
    seg_lines = []
    segid = -1
    id_nbest = 0
    for i, seg in enumerate(result['segments']):
        # import ipdb;ipdb.set_trace()
        if seg['id_nbest'] != id_nbest or seg['segid'] != segid:
            # start of a new segment or a new n-best
            if i != 0:
                seg_dict['text'] = ' '.join(seg_dict['text'].split())
                assert len(seg_dict['tokens']) == len(seg_dict['tokenids']) == len(seg_dict['tokens_logprobs'])
                seg_lines.append(seg_dict)
            id_nbest = seg['id_nbest']
            segid = seg['segid']
            seg_dict = dict()
            seg_dict['id'] = '{}_target1[{}]'.format(fileid, id_nbest)
            seg_dict['start_time'] = seg['start']
            seg_dict['end_time'] = seg['end']
            seg_dict['text'] = seg['text']
            seg_dict['temperature'] = seg['temperature']
            seg_dict['avg_logprob'] = seg['avg_logprob']
            seg_dict['sum_logprob'] = seg['sum_logprob']
            seg_dict['compression_ratio'] = seg['compression_ratio']
            seg_dict['no_speech_prob'] = seg['no_speech_prob']
            seg_dict['tokens'] = seg['tokens']
            seg_dict['tokenids'] = seg['tokenids']
            seg_dict['tokens_logprobs'] = seg['tokens_logprobs']
        else:
            # the same segments, one segment might have multiple chunks, merge the chunks
            # text, tokens, tokenids, tokens_logprobs
            seg_dict['end_time'] = seg['end']
            seg_dict['text'] += ' ' + seg['text']
            seg_dict['tokens'] += seg['tokens']
            seg_dict['tokenids'] += seg['tokenids']
            seg_dict['tokens_logprobs'] += seg['tokens_logprobs']
        if i == len(result['segments']) - 1:
            seg_dict['text'] = ' '.join(seg_dict['text'].split())
            assert len(seg_dict['tokens']) == len(seg_dict['tokenids']) == len(seg_dict['tokens_logprobs'])
            seg_lines.append(seg_dict)
    return seg_lines

def read_tokenlist(fpath):
    # one line in the input file
    with open(fpath, 'r', encoding='utf-8') as f:
        tokens = f.readlines()[0].strip()
    return tokens

def main ( args ):
    #------------------------------------------------------------------------------
    # read in command line arguments
    #------------------------------------------------------------------------------
    wavlistfile = args.wav_lst
    model_src = args.model
    model_dir = args.model_dir
    device_type = args.device
    num_device = args.num_device
    nbest = args.nbest
    suppress = args.suppress
    suppress_blank = args.suppress_blank
    notimestamps = args.notimestamps
    wordtimestamps = args.wordtimestamps
    condition_previous = args.dontconditionprevious
    no_speech_threshold = args.no_speech_threshold
    tokenlist = args.tokenlist
    tgtdir = os.path.join (args.outdir, "json")
    beam_size = args.beam_size

    print('passed device number: ', num_device)

    checkFileExists ( wavlistfile )

    makeDir (tgtdir, False)

    #------------------------------------------------------------------------------
    # save command line arguments to file
    #------------------------------------------------------------------------------
    makeCmdPath (tgtdir)

    #------------------------------------------------------------------------------
    # get items set up prior to running whisper transcription
    #------------------------------------------------------------------------------
    if suppress is True:
        if tokenlist:
            checkFileExists ( tokenlist )
            suppress_tokens = read_tokenlist( tokenlist )
        else:
            suppress_tokens = '0,3,5,6,11,13,30,62,492,526,553,960,986,1106,1399,1539,1600,1701,1906,2474,2637,3228,3548,4032,4210,7061,8348,9313,11496,12248,13531,13679,14988,16078,19056,21215,23141,24426,26214,28358,30543,44825'
        print('Suppress tokens: ', suppress_tokens)
    else:
        suppress_tokens = ''

    idlist, wavlist = read_wav_list(wavlistfile)

    ## Load the model
    print('loading whisper model: ', model_src)
    print('running on device: ', device_type)
    model = whisper.load_model(model_src, device=device_type, download_root=model_dir)

    #------------------------------------------------------------------------------
    # process each wav file
    #------------------------------------------------------------------------------
    posn = 0
    initial_prompt_stg=''
    for wav_path in tqdm(wavlist):
        fname = '.'.join(os.path.basename(wav_path).split('.')[:-1])   # ends with *wav, *mp3, *flac
        idname = idlist[posn]
        tgt_json = os.path.join ( tgtdir, idname + ".json" )

        if not os.path.exists (wav_path) is True:
            print('ERROR: wav not found: ', wav_path)
            continue

        ### Here the script call whisper transcribe
        with torch.no_grad():
            result = model.transcribe(wav_path, without_timestamps=notimestamps, beam_size=beam_size,no_speech_threshold=no_speech_threshold,word_timestamps=wordtimestamps, condition_on_previous_text=condition_previous,length_penalty=None,initial_prompt=None, fp16=(model.device!='cpu'), language='en', suppress_blank=suppress_blank)

        for i in range(len(result['segments'])):
            result['segments'][i]['attn_weights']=0

        with open(tgt_json, 'w', encoding='utf-8') as fp:
            json.dump(result, fp, ensure_ascii=False)

        posn += 1

    # convert json files to CTM
    basename = str(Path(wavlistfile).stem).split('.')[0]
    output_ctm = os.path.join (args.outdir, 'asr.ctm')        
    ctm_lines = json_to_ctm_lines ( tgtdir )

    # Sort ctm_lines based on the filename
    ctm_lines.sort(key=lambda x: x.split()[0])

    with open(output_ctm, 'w') as ctm_out:
        for line in ctm_lines:
            print(line, file=ctm_out)

if __name__ == '__main__':
    #------------------------------------------------------------------------------
    # arguments
    #------------------------------------------------------------------------------
    parser = argparse.ArgumentParser(description='Transcribe wav files in a wav list')
    parser.add_argument('--wav_lst', help='input wav list')
    parser.add_argument('--model', type=str, default='base.en', help='name of the pretrained model')
    parser.add_argument('--device', type=str, default='cpu', help='cpu or cuda')
    parser.add_argument('--num_device', type=int, default='-1', help='device number')
    parser.add_argument('--outdir', type=str, help='output directory to save the transcribed data in json format')
    parser.add_argument('--model_dir', type=str, default='models/pretrained_ckpts', help='path to load model')
    parser.add_argument('--nbest', type=int, default='0', help='output nbest with logprob for each token')
    parser.add_argument('--suppress', action='store_true', default=False, help='suppress special tokens like punctuation')
    parser.add_argument('--suppress_blank', action='store_true', default=False, help='suppress blank outputs')
    parser.add_argument('--notimestamps', action='store_true', default=False, help='run without_timestamps')
    parser.add_argument('--wordtimestamps', action='store_true', default=False, help='run with word timestamps')
    parser.add_argument('--tokenlist', type=str, default='', help='a file containing the comma separated tokens to be suppressed')
    parser.add_argument('--dontconditionprevious', action='store_false', default=True, help='do not condition on previous text')
    parser.add_argument('--no_speech_threshold', type=float, default='0.6', help='no speech threshold')
    parser.add_argument('--beam_size', type=int, default='5', help='beam_size')
    parser.add_argument('--initial_prompt_list', type=str, default='NULL', help='a file containing a set of initial prompts')
    args = parser.parse_args()
    main(args)

