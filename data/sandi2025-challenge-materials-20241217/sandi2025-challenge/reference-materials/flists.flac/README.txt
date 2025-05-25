Audio file lists

Assumes the data is installed into specific directories under data/

Description of files:

File format:
fileID[tab]path to flac file

${dataset}-asr.tsv     : list of files to use for the ASR task for dataset e.g. dev-asr.tsv
${dataset}-gec.tsv     : list of files to use for the GEC and SGECF tasks for dataset. This is a subset of the asr files. e.g. dev-gec.tsv
${dataset}-sla-P1.tsv  : list of files to use for test part 1 in SLA. This includes all asr files plus additional files.  e.g. dev-sla-P1.tsv.
${dataset}-sla-P3.tsv  : list of files to use for test part 3 in SLA. This includes all asr files plus additional files.  e.g. dev-sla-P3.tsv.
${dataset}-sla-P4.tsv  : list of files to use for test part 4 in SLA. This includes all asr files plus additional files.  e.g. dev-sla-P4.tsv.
${dataset}-sla-P5.tsv  : list of files to use for test part 5 in SLA. This includes all asr files plus additional files.  e.g. dev-sla-P5.tsv.
${dataset}-sla-overall.tsv : list of files with all parts for overall holistic scoring of SLA. This has files from all 4 parts. e.g. dev-sla-overall.tsv

N.B. for the train data set, some test submissions are incomplete so not included in the overall marks file


