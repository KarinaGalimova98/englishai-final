#!/bin/bash
#$ -S /bin/bash

# run WER scoring using the NIST Sclite tool

ALLARGS="$0 $@"
NUMARGS=$#

# EDIT SCRIPT HERE: set up sandi directory to your location
sandi="."

# set up reference and tools directories
tools_dir=$sandi/scoring-tools/wer-tools
ref_dir=$sandi/reference-materials

# set up environment
ENV=$sandi/envs/sandi-all-env.sh

# hard-wired for dev_scoring - command-line overwrite
glm=$ref_dir/glm/sandi-20241209.glm

# Function to print usage information
print_usage() {
    echo " Usage: $0 --stm filepath --ctm filepath --out_dir dirname [--glm filepath]"
    echo " --stm       STM file to use as scoring reference"
    echo " --ctm       CTM file to be scored"
    echo " --out_dir   Output scoring directory"
    echo " --glm       sclite GLM file for mapping word equivalencies (optional - default is to use glm in reference-materials/glm)"
    exit 100
}

# look for optional arguments
while [ $# -gt 0 ]; do
    key=$1
    case $key in
        --glm)
	    shift
        glm=$1
        shift
        ;;
        --stm)
	    shift
        stm=$1
        shift
        ;;
        --ctm)
        shift
        ctm=$1
        shift
        ;;
	--out_dir)
	    shift
        out_dir=$1
        shift
        ;;
	--help)
	    shift
	    print_usage
	    ;;
	*)	    
    POSITIONAL+=("$1")
    shift
    ;;
    esac
done
set -- "${POSITIONAL[@]}"


if [[ $# -gt 0 ]] || [[ $NUMARGS -lt 1 ]]; then
    print_usage
fi

# Check file/directory existence and flag requirements
if [[ -z $stm ]] || [[ -z $ctm ]] || [[ -z $out_dir ]]; then
    print_usage
fi

if [ ! -f $stm ]; then
    echo "ERROR: STM file not found: $stm"
    exit 100
fi
if [ ! -f $ctm ]; then
    echo "ERROR: CTM file not found: $ctm"
    exit 100
fi
if [ -d $out_dir ]; then
    echo "ERROR: scoring directory $out_dir exists. Delete to run"
    exit 100
fi
if [ ! -f $glm ]; then
    echo "ERROR: GLM not found: $glm"
    exit 100
fi

# Cache command line call
cmdfile=CMDs/$out_dir/run-wer-scoring.cmds
mkdir -p CMDs/$out_dir
echo $ALLARGS >> $cmdfile
echo "------------------------------------------------------------------------" >> $cmdfile

# source the environment
source $ENV

# Print the arguments to verify (optional)
echo "Reference STM   : ${stm}"
echo "CTM to score    : ${ctm}"
echo "Output directory: ${out_dir}"

# make the scoring output directory
score_ref_dir=$out_dir/ref
score_hyp_dir=$out_dir/hyp
mkdir -p $score_ref_dir
mkdir -p $score_hyp_dir
# make a directory to store log output from scoring
log_dir=$out_dir/LOGs 
mkdir -p $log_dir

# Copy CTM and STM to output directories
# sort and remove any files from CTM not in the STM
# merge contiguous phrases in STM
echo "Set up CTM and STM for scoring"
stm_base_name=$(basename "$stm")
ctm_base_name=$(basename "$ctm")

echo "Ensure CTM only has files to be scored and in order"
python $tools_dir/sort_subset_ctm.py --input_ctm $ctm --input_stm $stm --output_ctm $score_hyp_dir/$ctm_base_name
if [ ! -f $score_hyp_dir/$ctm_base_name ]; then
    echo "ERROR: CTM not created: $score_hyp_dir/$ctm_base_name"
    exit 100
fi

echo "Merge contiguous phrases in STM"
python $tools_dir/mergescorestmsegs.py $stm $score_ref_dir/$stm_base_name
if [ ! -f $score_ref_dir/$stm_base_name ]; then
    echo "ERROR: STM not created: $score_ref_dir/$stm_base_name"
    exit 100
fi

# Apply GLM filtering if GLM provided
ref_file=$score_ref_dir/$stm_base_name
hyp_file=$score_hyp_dir/$ctm_base_name

echo "Apply GLM filtering"
LOG=$log_dir/glm_filter.log
cmd_gf="python $tools_dir/glm_filter.py --glm $glm --stm $ref_file --ctm $hyp_file"
eval "$cmd_gf" >> "$LOG" 2>&1
echo $cmd_gf

# Check if the python script executed successfully 
ref_file=$score_ref_dir/$stm_base_name.filt
hyp_file=$score_hyp_dir/$ctm_base_name.filt
if [ ! -f $ref_file ]; then
    echo "ERROR: filter file not created by glm_filter: $ref_file"
    exit 100
fi
if [ ! -f $hyp_file ]; then
    echo "ERROR: filter file not created by glm_filter: $hyp_file"
    exit 100
fi

# Run sclite on the original or filtered CTM and STM files
LOG=$log_dir/sclite.log
if [ -f $LOG ]; then
    \rm $LOG
fi

echo "Writing scoring report to '$score_hyp_dir'"

$tools_dir/sctk-2.4.9/bin/sclite -r "$ref_file" stm -h "$hyp_file" ctm -F -D -o sum rsum sgml lur dtl pra |& tee $LOG

if [ ! -f ${hyp_file}.sys ]; then
    echo "ERROR: sclite scoring file not created - see $LOG"
    exit 100
fi

echo "Scoring complete - see $hyp_file.*"
grep "SPKR" $hyp_file.sys
grep "Sum/Avg" $hyp_file.sys




