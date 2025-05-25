Speak & Improve Challenge 2025
==============================

Directory structure:
baseline-pipeline/   : scripts and code to run the baseline pipeline
check-pipeline.sh    : script to run all commands detailed below to run and check the software is working as expected
data/                : audio data should be unpacked or linked in here (this has to be downloaded separately)
envs/                : pointers to conda environments required to run code
README-install-dataset.txt : describes steps to take to complete installation of the Challenge components
README.txt           : this file
reference-materials/ : reference files (marked up annotations, file lists, GLM for WER scoring, SLA marks and STMs)
sandi-models/        : models supplied for the Challenge pipeline which should be unpacked or linked in here (this has to be downloaded separately)
scoring-tools/       : scripts and code to run the 4 evaluation classes
setup.sh             : script to set-up a linked copy of the challenge directory

Instructions for set-up for experiments
=======================================
1. Link directories to your local working space
linux> $DOWNLOAD_DIR/sandi2025-challenge/setup.sh --path $DOWNLOAD_DIR

2, Check the following are set up or see README-install-dataset.txt for instructions
 a. Audio data should be linked into ./data/
 b. Baseline pipeline models should be linked into:
       ./sandi-models/bert-sla/
       ./sandi-models/dd/
       ./sandi-models/gec/
 c. The environment shell scripts should point to your local miniconda installation
       ./envs/sandi-all-env.sh
       ./envs/sandi-dd-env.sh

Reference materials
===================
Files are generally labelled starting with the name of the data-set:
 dev        : Development set - use for testing and tuning prior to the Challenge evaluation
 dev-subset : 2 test submissions from the development set selected to illustrate the various stages of the pipeline (see below)
 train      : Train set - use for training

Task labels are used to identify different subsets of each data set:
 asr         : data with manual disfluent transcriptions for use in ASR training and test
 gec         : data with grammatical error corrected fluent transcriptions for use in GEC/SGECF training and test
 sla	     : data for use in spoken language assessment. This is further divided as:
 sla-P#      : data for use in spoken language assessment of part # (parts 1, 3, 4 and 5 included)
 sla-overall : data for use in overall holistic spoken language assessment

Additional labels in file names:
 fluent      : fluent data transcriptions i.e. disfluencies removed but contains original spoken grammatical errors
 phrase      : data is labelled at phrase level (default is utterance). Used for GEC/SGECF
 
reference-materials/
  annotations/      : json files with marked up annotations of the Speak & Improve (S&I) Corpus 2025
  docs/             : papers describing the S&I Corpus 2025 and the S&I Challenge 2025
  flists.flac/      : audio file lists for different data sets and tasks
  glm/              : global mapping (GLM) file for use in NIST sclite WER scoring
  pre-norm/	    : pre-normalised outputs from the baseline ASR system (OpenAI Whisper small)
  sla/		    : spoken language assessment (SLA) proficiency scores
  stms/		    : STMs for scoring; manual (disfluent), fluent and GEC transcriptions. Includes time stamp information at phrase level.
  
See README.txt in each reference-materials directory for more detailed information

Instructions for running
========================
Examples are shown for the (very) small dev-subset
To run all the commands shown below:
linux> ./check-pipeline.sh

Command line arguments for tools will be cached under the directory CMDs/ that will be created
when programmes are run

ASR decodes
===========
a. Run OpenAI Whisper decode for each file set in reference-materials/flists.flac e.g.

linux> ./baseline-pipeline/run-scripts/run-asr-decode.sh --flist reference-materials/flists.flac/dev-subset-asr.tsv \
--model_type small --out_dir dev-subset/asr

  - output is CTM file of ASR transcripts to be used in future stages:
      dev-subset/asr/decode/dev-subset-asr/asr.ctm

Note: for larger data sets which have been split into smaller subsets we recommend running to the same output directory
 e.g. for dev
linux> ./baseline-pipeline/run-scripts/run-asr-decode.sh --flist reference-materials/flists.flac/dev-asr.tsv \
--model_type small --out_dir dev/asr
    CTM output: dev/asr/decode/dev-asr/asr.ctm
    
linux> ./baseline-pipeline/run-scripts/run-asr-decode.sh --flist reference-materials/flists.flac/dev-sla-only.tsv \
--model_type small --out_dir dev/asr
    CTM output: dev/asr/decode/dev-sla-only/asr.ctm
  
ASR scoring
===========
a. Convert ASR output CTMs into normalised form for ASR WER scoring e.g.

linux> ./baseline-pipeline/run-scripts/run-asr-to-task-input.sh --input_ctms dev-subset/asr/decode/dev-subset-asr/asr.ctm \
--flist reference-materials/flists.flac/dev-subset-asr.tsv --task asr --out_dir dev-subset/asr

   - output is ASR normalised CTM for dev-subset data set for input to ASR WER scoring
      dev-subset/asr/norm/asr.ctm

b. Score CTM with WER e.g.

linux> ./scoring-tools/run-scripts/run-wer-scoring.sh --stm reference-materials/stms/dev-subset-asr.stm \
--ctm dev-subset/asr/asr.ctm --out_dir dev-subset/asr/wer-scoring

   - output scoring report to directory dev-subset/asr/wer-scoring/hyp/
      a) asr.ctm.filt.sys : system summary percentages by submission. Sum/Avg is the overall WER for the test set
      b) asr.ctm.filt.dtl : detailed overall report of errors made
      c) asr.ctm.filt.lur : WER by category: audio quality; grade level; test part
      d) asr.ctm.filt.pra : dump of alignment of reference and hypothesis texts
      e) asr.ctm.filt.raw : raw counts of number of deletions, insertions, substitutions etc
      f) asr.ctm.filt.sgml : SGML of scoring

Expected overall WER result (from dev-subset/asr/wer-scoring/hyp/asr.ctm.filt.sys)
| SPKR         | # Snt # Wrd | Corr    Sub    Del    Ins    Err  S.Err |  NCE   |
| Sum/Avg      |   22    956 | 91.7    3.2    5.0    1.8   10.0   86.4 | -0.035 |

Spoken Language Assessment (SLA)
================================
a. Convert ASR output CTM(s) into normalised forms for SLA scoring
- do for each of the 4 test parts (P1, P3, P4, P5)

linux> ./baseline-pipeline/run-scripts/run-asr-to-task-input.sh --input_ctms dev-subset/asr/decode/dev-subset-asr/asr.ctm \
--flist reference-materials/flists.flac/dev-subset-sla-P1.tsv --task sla-P1 --out_dir dev-subset/sla

   - output
      dev-subset/sla/norm/sla-P1.ctm : ASR CTM normalised for SLA for part 1 utterances
      
linux> ./baseline-pipeline/run-scripts/run-asr-to-task-input.sh --input_ctms dev-subset/asr/decode/dev-subset-asr/asr.ctm \
--flist reference-materials/flists.flac/dev-subset-sla-P3.tsv --task sla-P3 --out_dir dev-subset/sla

  - output
      dev-subset/sla/norm/sla-P3.ctm : ASR CTM normalised for SLA for part 3 utterances
      
linux> ./baseline-pipeline/run-scripts/run-asr-to-task-input.sh --input_ctms dev-subset/asr/decode/dev-subset-asr/asr.ctm \
--flist reference-materials/flists.flac/dev-subset-sla-P4.tsv --task sla-P4 --out_dir dev-subset/sla

  - output
      dev-subset/sla/norm/sla-P4.ctm : ASR CTM normalised for SLA for part 4 utterances  
      
linux> ./baseline-pipeline/run-scripts/run-asr-to-task-input.sh --input_ctms dev-subset/asr/decode/dev-subset-asr/asr.ctm \
--flist reference-materials/flists.flac/dev-subset-sla-P5.tsv --task sla-P5 --out_dir dev-subset/sla

  - output
      dev-subset/sla/norm/sla-P5.ctm : ASR CTM normalised for SLA for part 5 utterances  
      
b. Run SLA
- runs SLA on a test part level for each of the 4 parts (P1,P3,P4,P5) and then combines scores to produce
  the overall test score prediction
- predictions are calibrated

linux> ./baseline-pipeline/run-scripts/run-sla.sh --ctm_dir dev-subset/sla/norm --model_dir sandi-models/bert-sla \
--out_dir dev-subset/sla --test dev-subset

   - output
      dev-subset/sla/sla.tsv : calibrated holistic test level SLA predictions

Note:
1. Due to the small size of the sample calibration will work exactly

c. Score SLA

linux> ./scoring-tools/run-scripts/run-sla-scoring.sh --pred dev-subset/sla/sla.tsv --test dev-subset-sla-overall \
--out_dir dev-subset/sla 

   - output
      dev-subset/sla/result.dev-subset-sla-overall.txt : SLA scoring result

Expected output (note, small size for calibration causes unnaturally good results!)
Infile dev-subset/sla/sla.tsv:
RMSE: 0.000, PCC: 1.000, SRC: 1.000, KRC: 1.000, LESS05: 100.0%, LESS1: 100.0%

    RMSE = Root Mean Square Error
    PCC  = Pearson Correlation Coefficient
    SRC  = Spearman Rank Coefficient
    KRC  = Kendall Rank Coefficient
    LESS05 = percentage of predictions <= 0.5 of the reference mark
    LESS1  = percentage of predictions <= 1.0 of the reference mark

Grammatical Error Correction (GEC)
==================================
a. Convert ASR output CTM(s) into normalised form for disfluency detection (DD)/GEC pipeline

linux> ./baseline-pipeline/run-scripts/run-asr-to-task-input.sh --input_ctms dev-subset/asr/decode/dev-subset-asr/asr.ctm \
--flist reference-materials/flists.flac/dev-subset-gec.tsv --task gec --out_dir dev-subset/gec

   - output is ASR CTM normalised for input to DD 
      dev-subset/gec/norm/gec.ctm

b. Run disfluency detection followed by grammatical error correction

linux> ./baseline-pipeline/run-scripts/run-gec.sh --ctm dev-subset/gec/norm/gec.ctm --dd_model sandi-models/dd/dd_model \
--gec_model sandi-models/gec/gec_model --out_dir dev-subset/gec

  - outputs:
     dev-subset/gec/fluent.ctm : fluent ASR transcript, post disfluency detection - will be used in SGECF scoring
     dev-subset/gec/gec.ctm    : CTM of grammatically error corrected fluent transcript
                                 - will be used in spoken GEC WER and SGECF scoring

c. Score Spoken GEC
- generate the WER between the specifed CTM and the reference GEC text STM

linux> ./scoring-tools/run-scripts/run-wer-scoring.sh --stm reference-materials/stms/dev-subset-gec.stm \
--ctm dev-subset/gec/gec.ctm --out_dir dev-subset/gec/wer-scoring

   - output scoring report to directory dev-subset/gec/wer-scoring/hyp/
      a) gec.ctm.filt.sys : system summary percentages by submission. Sum/Avg is the overall WER for the test set
      b) gec.ctm.filt.dtl : detailed overall report of errors made
      c) gec.ctm.filt.lur : WER by category: audio quality; grade level; test part
      d) gec.ctm.filt.pra : dump of alignment of reference and hypothesis texts
      e) gec.ctm.filt.raw : raw counts of number of deletions, insertions, substitutions etc
      f) gec.ctm.filt.sgml : SGML of scorin

Expected overall WER result (from dev-subset/gec/wer-scoring/hyp/asr.ctm.filt.sys)
| SPKR         | # Snt # Wrd | Corr    Sub    Del    Ins    Err  S.Err |  NCE   |
| Sum/Avg      |   22    667 | 87.3    6.1    6.6    4.5   17.2   95.5 | -0.005 |

d. Score Spoken GEC Feedback (SGECF)
- generate the F0.5 score using Spoken ERRANT

linux> ./scoring-tools/run-scripts/run-sgecf-scoring.sh --flt_stm reference-materials/stms/dev-subset-fluent.stm \
--gec_stm reference-materials/stms/dev-subset-gec.stm --flt_ctm dev-subset/gec/fluent.ctm \
--gec_ctm dev-subset/gec/gec.ctm --out_dir dev-subset/gec/sgecf-scoring

  - output SGECF scoring in dev-subset/gec/sgecf-scoring/result.txt (precision, recall, F_0.5)

Expected output:
P:	0.323
R	0.145
F0.5:	0.259

