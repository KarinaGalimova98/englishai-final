#!/bin/bash

# This is the pipeline for Spoken Language Assessment (SLA) task.
#  Step1: Run the SLA on a test part level - normalise CTM to responses and run inference
#  Step2: Calibrate the predictions
#  Step3: Average per-part predictions to get overall predictions for the submissions
#
# Baseline models are provided for each part of the submission (see sandi-models/sla directory).

ALLARGS="$0 $@"

# EDIT SCRIPT HERE: set up sandi directory to your location
sandi="."

# set up reference and tools directories
tools_dir=$sandi/baseline-pipeline
ref_dir=$sandi/reference-materials

# set up environment
ENV=$sandi/envs/sandi-all-env.sh

testset=dev

# Function to print usage information
# (could be expanded to include setting above optionally)
print_usage() {
    echo "Usage: $0 --ctm_dir <ctm_dirpath> --model_dir <model_dirpath> --out_dir <output_path>"
    echo "  --ctm_dir      : Path to the input CTM directory."
    echo "  --model_dir    : Directory of BERT models to use for inference."
    echo "  --out_dir      : Top directory name for output."
    echo "  --test         : (Optional) Test set name (default: dev)"
    echo "  --help         : Display this help message."
    exit 100
}

parse_long_options() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --ctm_dir)
                shift
                ctm_dir=$1
		shift
                ;;
            --model_dir)
                shift
                model_dir=$1
		shift
                ;;
            --out_dir)
                shift
                out_dir=$1
		shift
                ;;
            --test)
                shift
                testset=$1
		shift
                ;;
            --help)
                print_usage
                ;;
            *)
                echo "Unknown option: $1"
                print_usage
                ;;
        esac
    done
}

# Call the function to parse long options
parse_long_options "$@"

# Check if required arguments are provided
if [[ -z "$ctm_dir" ]] || [[ -z "$model_dir" ]] || [[ -z "$out_dir" ]] ; then
    print_usage
fi

# Check inputs exist
if [ ! -d $ctm_dir ]; then
    echo "ERROR: CTM directory $ctm_dir not found"
    exit 100
fi
if [ ! -d $model_dir ]; then
    echo "ERROR: CTM directory $model_dir not found"
    exit 100
fi    

pred_dir=$out_dir/predictions
if [ -d $pred_dir ]; then
    \rm -r $pred_dir
fi

# Create CMDs/ directory if it doesn't exist
mkdir -p CMDs/$out_dir

# Log the command-line arguments
cmdfile=CMDs/$out_dir/run-sla.sh.cmds
echo "$ALLARGS" >> "$cmdfile"
echo "------------------------------------------------------------------------" >> "$cmdfile"

# Print the arguments to verify (optional)
echo "CTM input dir: ${ctm_dir}"
echo "SLA BERT model dir: ${model_dir}"
echo "Output directory: ${out_dir}"

mkdir -p $out_dir

log_dir=$out_dir/LOGs/
mkdir -p $log_dir
echo "Log directory: ${log_dir}"

source $ENV

### Step1: Run the SLA - run inference on individual part
###        - returns uncalibrated predictions
for part in 1 3 4 5;do
    echo "Running inference for part $part"
    python3 $tools_dir/sla-tools/inference_sla.py \
	--model $model_dir/bert-P${part}.th \
	--ctm_file $ctm_dir/sla-P${part}.ctm \
	--output_file $pred_dir/sla-P${part}.predictions.tsv \
        --part ${part} |& tee $log_dir/sla-P${part}.predictions.LOG

    if [ ! -f $pred_dir/sla-P${part}.predictions.tsv ]; then
	echo "ERROR: predictions not found: $pred_dir/sla-P${part}.predictions.tsv"
	exit 100
    fi
done

### Step2: Calibrate the predictions
for part in 1 3 4 5; do
    echo "Running calibration for part $part"
    python3 $tools_dir/sla-tools/calibrate.py \
	    --pred $pred_dir/sla-P${part}.predictions.tsv \
	    --ref $ref_dir/sla-marks/${testset}-sla-P${part}.tsv \
	    --calib_coeffs $out_dir/calibration/sla-P${part}.calib_coeffs.tsv
    
    if [ ! -f $pred_dir/sla-P${part}.predictions_calibrated.tsv ]; then
	echo "ERROR: predictions not found: $pred_dir/sla-P${part}.predictions_calibrated.tsv"
	exit 100
    fi
done

### Step3: Average per-part predictions to get overall predictions for the submissions
# uncalibrated results
echo "Computing overall submission predictions"
python3 $tools_dir/sla-tools/part2submission.py \
	--input "$pred_dir/sla-P1.predictions.tsv $pred_dir/sla-P3.predictions.tsv $pred_dir/sla-P4.predictions.tsv $pred_dir/sla-P5.predictions.tsv" \
	--output $pred_dir/sla-overall.predictions.tsv

if [ ! -f $pred_dir/sla-overall.predictions.tsv ]; then
    echo "ERROR: overall predictions $pred_dir/sla-overall.predictions.tsv not found"
    exit 100
fi

# calibrated results, average calibrated per-part predictions then calibrate again
echo "Computing calibrated overall submission predictions"
python3 $tools_dir/sla-tools/part2submission.py \
	--input "$pred_dir/sla-P1.predictions_calibrated.tsv $pred_dir/sla-P3.predictions_calibrated.tsv $pred_dir/sla-P4.predictions_calibrated.tsv $pred_dir/sla-P5.predictions_calibrated.tsv" \
	--output $pred_dir/sla-overall.predictions_part.tsv

if [ ! -f $pred_dir/sla-overall.predictions_part.tsv ]; then
    echo "ERROR: overall predictions $pred_dir/sla-overall.predictions_part.tsv not found"
    exit 100
fi

python3 $tools_dir/sla-tools/calibrate.py \
	--pred $pred_dir/sla-overall.predictions_part.tsv \
	--ref $ref_dir/sla-marks/${testset}-sla-overall.tsv \
	--calib_coeffs $out_dir/calibration/sla-overall.calib_coeffs.tsv

if [ ! -f $pred_dir/sla-overall.predictions_part_calibrated.tsv ]; then
    echo "ERROR: overall calibrated predictions $pred_dir/sla-overall.predictions_part_calibrated.tsv not found"
    exit 100
fi

\cp $pred_dir/sla-overall.predictions_part_calibrated.tsv $out_dir/sla.tsv

echo "SLA complete. Final overall holistic predictions: $out_dir/sla.tsv"




