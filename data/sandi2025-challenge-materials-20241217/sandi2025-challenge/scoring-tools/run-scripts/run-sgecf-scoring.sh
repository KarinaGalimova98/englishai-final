#!/bin/bash
#$ -S /bin/bash

# run GEC scoring 

ALLARGS="$0 $@"
NUMARGS=$#

# EDIT SCRIPT HERE: set up sandi directory to your location
sandi=.

# set up reference and tools directories
tools_dir=$sandi/scoring-tools/sgecf-tools
ref_dir=$sandi/reference-materials

# set up environment
ENV=$sandi/envs/sandi-all-env.sh

# hard-wired for dev_scoring - command-line overwrite
flt_stm=$ref_dir/stms/dev-fluent.stm
gec_stm=$ref_dir/stms/dev-gec.stm

# Function to print usage information
# (could be expanded to include setting above optionally)
print_usage() {
    echo " Usage: $0 [--edit_detail] [--flt_stm <fluent_stm_path>] [--gec_stm <gec_stm_path>] --flt_ctm <fluent_ctm_path> --gec_ctm <gec_ctm_path> --out_dir <dir_path>"
    echo " --edit_detail : (Optional) Produce breakdown by edit type"
    echo " --flt_stm     : (Optional) Fluent STM file to use as scoring reference (default: dev)" 
    echo " --gec_stm     : (Optional) GEC STM file to use as scoring reference (default: dev)"
    echo " --flt_ctm     : Fluent CTM file"
    echo " --gec_ctm     : GEC CTM file"
    echo " --out_dir     : Output scoring directory"
    exit 100
}

ERRANT_ARGS=""

parse_long_options() {
    while [[ $# -gt 0 ]]; do
        case $1 in
        --edit_detail)
	    shift
	    ERRANT_ARGS="$ERRANT_ARGS --split_edit_type"
            ;;
        --gec_stm)
	    shift
        gec_stm=$1
        shift
        ;;
        --flt_stm)
	    shift
        flt_stm=$1
        shift
        ;;
        --gec_ctm)
	    shift
        gec_ctm=$1
        shift
        ;;
        --flt_ctm)
	    shift
        flt_ctm=$1
        shift
        ;;
	--out_dir)
	    shift
        out_dir=$1
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

# Check file/directory existence and flag requirements
if [[ -z $flt_ctm ]] || [[ -z $gec_ctm ]] || [[ -z $out_dir ]]; then
    print_usage
fi

for f in $gec_stm $flt_stm $gec_ctm $flt_ctm;
do
    if [ ! -f $f ]; then
	echo "ERROR: file not found: $f"
	exit 100
    fi
done
if [ -f $out_dir/result.txt ]; then
    echo "ERROR: scoring directory file $out_dir/result.txt exists. Delete to run"
    exit 100
fi
if [ ! -z $glm ] && [ ! -f $glm ]; then
    echo "ERROR: GLM not found: $glm"
    exit 100
fi

# Cache command line call
cmdfile=CMDs/$out_dir/run-sgecf-scoring.cmds
mkdir -p CMDs/$out_dir
echo $ALLARGS >> $cmdfile
echo "------------------------------------------------------------------------" >> $cmdfile

# source the environment
source $ENV

# Print the arguments to verify (optional)
echo "Reference fluent STM   : ${flt_stm}"
echo "Reference GEC STM      : ${gec_stm}"
echo "Fluent CTM to score    : ${flt_ctm}"
echo "Fluent CTM to score    : ${gec_ctm}"
echo "Output directory: ${out_dir}"


# make the scoring output directory and workspace
errant_dir=$out_dir/errant
mkdir -p $errant_dir
log_dir=$out_dir/LOGs
mkdir -p $log_dir

### Step1: generate errant-files required for scoring
echo "Step1: Create files required for ERRANT scoring"
python3 $tools_dir/create_files_for_errant.py --flt_stm $flt_stm --flt_ctm $flt_ctm --gec_stm $gec_stm --gec_ctm $gec_ctm --ref_src $errant_dir/flt_stm.txt --hyp_src $errant_dir/flt_ctm.txt --ref_tgt $errant_dir/gec_stm.txt --hyp_tgt $errant_dir/gec_ctm.txt

if [[ ! -f $errant_dir/gec_stm.txt ]] || [[ ! -f $errant_dir/gec_ctm.txt ]]; then
    echo "ERROR: files not created as expected in $errant_dir prior to ERRANT scoring"
    exit 100
fi

### Step2: run errant-scoring
echo "Step2: Run ERRANT scoring"
python3 $tools_dir/spoken_errant.py $ERRANT_ARGS --ref_asr $errant_dir/flt_stm.txt --hyp_asr $errant_dir/flt_ctm.txt --ref_gec $errant_dir/gec_stm.txt --hyp_gec $errant_dir/gec_ctm.txt > $out_dir/result.txt

if [ ! -f $out_dir/result.txt ]; then
    echo "ERROR: result $out_dir/result.txt not found"
    exit 100
fi

echo "SGECF scoring complete. Result in $out_dir/result.txt"
tail -3 $out_dir/result.txt





