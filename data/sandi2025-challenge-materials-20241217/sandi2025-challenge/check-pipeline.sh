#!/bin/bash

if [ ! -e data/flac ]; then
    echo "ERROR: is the data directory setup as expected?"
    exit 100
fi
if [[ ! -e sandi-models/bert-sla ]] || [[ ! -e sandi-models/dd ]] || [[ ! -e sandi-models/gec ]]; then
    echo "ERROR: check the sandi-models/ directory has all models present (bert-sla/, dd/, gec/)"
    exit 100
fi


./baseline-pipeline/run-scripts/run-asr-decode.sh --flist reference-materials/flists.flac/dev-subset-asr.tsv \
						  --model_type small --out_dir dev-subset/asr

./baseline-pipeline/run-scripts/run-asr-to-task-input.sh --input_ctms dev-subset/asr/decode/dev-subset-asr/asr.ctm \
							 --flist reference-materials/flists.flac/dev-subset-asr.tsv \
							 --task asr --out_dir dev-subset/asr

./scoring-tools/run-scripts/run-wer-scoring.sh --stm reference-materials/stms/dev-subset-asr.stm \
					       --ctm dev-subset/asr/asr.ctm --out_dir dev-subset/asr/wer-scoring

./baseline-pipeline/run-scripts/run-asr-to-task-input.sh --input_ctms dev-subset/asr/decode/dev-subset-asr/asr.ctm \
							 --flist reference-materials/flists.flac/dev-subset-sla-P1.tsv \
							 --task sla-P1 --out_dir dev-subset/sla

./baseline-pipeline/run-scripts/run-asr-to-task-input.sh --input_ctms dev-subset/asr/decode/dev-subset-asr/asr.ctm \
							 --flist reference-materials/flists.flac/dev-subset-sla-P3.tsv \
							 --task sla-P3 --out_dir dev-subset/sla

./baseline-pipeline/run-scripts/run-asr-to-task-input.sh --input_ctms dev-subset/asr/decode/dev-subset-asr/asr.ctm \
							 --flist reference-materials/flists.flac/dev-subset-sla-P4.tsv \
							 --task sla-P4 --out_dir dev-subset/sla

./baseline-pipeline/run-scripts/run-asr-to-task-input.sh --input_ctms dev-subset/asr/decode/dev-subset-asr/asr.ctm \
							 --flist reference-materials/flists.flac/dev-subset-sla-P5.tsv \
							 --task sla-P5 --out_dir dev-subset/sla

./baseline-pipeline/run-scripts/run-sla.sh --ctm_dir dev-subset/sla/norm --model_dir sandi-models/bert-sla \
					   --out_dir dev-subset/sla --test dev-subset

./scoring-tools/run-scripts/run-sla-scoring.sh --pred dev-subset/sla/sla.tsv --test dev-subset-sla-overall \
					       --out_dir dev-subset/sla

./baseline-pipeline/run-scripts/run-asr-to-task-input.sh --input_ctms dev-subset/asr/decode/dev-subset-asr/asr.ctm \
							 --flist reference-materials/flists.flac/dev-subset-gec.tsv \
							 --task gec --out_dir dev-subset/gec

./baseline-pipeline/run-scripts/run-gec.sh --ctm dev-subset/gec/norm/gec.ctm --dd_model sandi-models/dd/dd_model \
					   --gec_model sandi-models/gec/gec_model --out_dir dev-subset/gec

./scoring-tools/run-scripts/run-wer-scoring.sh --stm reference-materials/stms/dev-subset-gec.stm \
					       --ctm dev-subset/gec/gec.ctm --out_dir dev-subset/gec/wer-scoring

./scoring-tools/run-scripts/run-sgecf-scoring.sh --flt_stm reference-materials/stms/dev-subset-fluent.stm \
						 --gec_stm reference-materials/stms/dev-subset-gec.stm --flt_ctm dev-subset/gec/fluent.ctm \
						 --gec_ctm dev-subset/gec/gec.ctm --out_dir dev-subset/gec/sgecf-scoring













