#!/bin/bash
#$ -S /bin/bash

# run SLA scoring across all parts and overall
# individual SLA scoring can be run with the python tool scoring-tools/sla-tools/score-sla.py

ALLARGS="$0 $@"

# EDIT SCRIPT HERE: set up sandi directory to your location
sandi="."

# set up reference and tools directories
tools_dir=$sandi/scoring-tools/sla-tools
ref_dir=$sandi/reference-materials/sla-marks

# set up environment
ENV=$sandi/envs/sandi-all-env.sh

testid=dev-sla-overall

# Function to print usage information
# (could be expanded to include setting above optionally)
print_usage() {
    echo "Usage: $0 --pred <predictions_filepath> --out_dir <dir_path>"
    echo "  --pred       : Path to SLA predictions to score."
    echo "  --out_dir    : Output directory for scores."
    echo "  --test       : (Optional) Test set ID (default: dev-sla-overall)"
    echo "  --help       : Display this help message."
    exit 100
}

parse_long_options() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --pred)
                shift
                pred_file=$1
		shift
                ;;
            --out_dir)
                shift
                out_dir=$1
		shift
                ;;
            --test)
                shift
                testid=$1
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
if [[ -z "$pred_file" ]] || [[ -z "$out_dir" ]] ; then
    print_usage
fi
if [ ! -f $pred_file ]; then
    echo "ERROR: predictions file $pred_file not found"
    exit 100
fi
ref_file=$ref_dir/${testid}.tsv
if [ ! -f $ref_file ]; then
    echo "ERROR: reference file $ref_file not found"
    exit 100
fi

# Create CMDs/ directory if it doesn't exist
mkdir -p CMDs/$out_dir

# Cache the command-line arguments
cmdfile=CMDs/$out_dir/run-sla-scoring.sh.cmds
echo "$ALLARGS" >> "$cmdfile"
echo "------------------------------------------------------------------------" >> "$cmdfile"

# source the environment
source $ENV

# Print the arguments to verify (optional)
echo "Predictions file  : ${pred_file}"
echo "Reference file    : ${ref_file}"
echo "Output file       : ${out_dir}/result.${testid}.txt"

mkdir -p $out_dir
log_dir=$out_dir/LOGs
echo "Log directory     : ${log_dir}"

### Evaluate SLA predictions
python3 $tools_dir/score-sla.py \
	--pred $pred_file \
	--ref $ref_file > $out_dir/result.${testid}.txt

echo "\n"
echo "Scoring complete"
cat $out_dir/result.${testid}.txt
