#!/bin/bash

# run Whisper decode on selected file list
# produces Whisper json output which is combined into unnormalised CTM file
# in ${out_dir}/decode/small/${flist_id}/

ALLARGS="$0 $@"
# EDIT SCRIPT HERE: set up sandi directory to your location
sandi="."

# set up reference and tools directories
tools_dir=$sandi/baseline-pipeline
ref_dir=$sandi/reference-materials

# set up environment
ENV=$sandi/envs/sandi-all-env.sh

# Function to print usage information
print_usage() {
    echo "Usage: $0 --flist <file_list> --model_type <model_type> --out_dir <top_out_dir>"
    echo "  --flist        : Path to the file list"
    echo "  --model_type   : Type of the model"
    echo "  --out_dir      : Top directory name for output."
    echo "  --cpu          : (Optional) run on CPU."
    echo "  --num_device   : (Optional) number of GPU device to run on."
    echo "  --help         : Display this help message."
    exit 100
}

# Default values for optional arguments
num_device=0

# Function to parse long options
parse_long_options() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --flist)
                shift
                flist=$1
		shift
                ;;
            --model_type)
                shift
                model_type=$1
		shift
                ;;
            --out_dir)
                shift
                top_out_dir=$1
		shift
                ;;
            --cpu)
                shift
                cpu=1
                ;;
            --num_device)
                shift
                num_device=$1
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
if [[ -z "$flist" ]] || [[ -z "$model_type" ]] || [[ -z "$top_out_dir" ]] ; then
    print_usage
fi

filename=$(basename "$flist" .tsv)

decode_dir=decode/${filename}
out_dir=${top_out_dir}/${decode_dir}

# Create CMDs/ directory if it doesn't exist
mkdir -p CMDs/$out_dir

# Cache the command-line arguments
cmdfile=CMDs/$top_out_dir/run-asr-decode.sh.cmds
echo "$ALLARGS" >> "$cmdfile"
echo "------------------------------------------------------------------------" >> "$cmdfile"

# source the environment
source $ENV

# Print the arguments to verify (optional)
echo "File list: ${flist}"
echo "Model type: ${model_type}"
echo "Output directory: ${out_dir}"

mkdir -p $out_dir
log_dir=$top_out_dir/LOGs/${decode_dir}
mkdir -p $log_dir

echo "Log directory: ${log_dir}"
echo "Whisper transcribe log: ${log_dir}/whisper_transcribe.log"

if [[ ! -z $cpu ]]; then
    num_device=-1
    device='cpu'
elif [[ ! -z "$CUDA_VISIBLE_DEVICES" ]] ; then
    num_device=$CUDA_VISIBLE_DEVICES
    device='cuda'
else
    export CUDA_VISIBLE_DEVICES=$num_device
    num_device=$num_device
    device='cuda'
fi

python $tools_dir/asr-tools/whisper_transcribe.py \
                            --wordtimestamps \
                            --suppress_blank \
                            --beam_size 5 \
                            --model $model_type \
                            --wav_lst $flist \
                            --device $device \
                            --num_device $num_device \
                            --outdir ${out_dir} \
                            --dontconditionprevious |& tee ${log_dir}/whisper_transcribe.log

echo "Decoding complete for $flist"



