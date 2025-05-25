#!/bin/bash

# set-up your local working space to run the challenge

ALLARGS="$0 $@"

# Function to print usage information
print_usage() {
    echo "Usage: $0 --path sandi2025-challenge-path"
    echo "  --path  : Path to the main install on your local system of sandi2025-challenge"
    echo "  --help  : Display this help message."
    exit 100
}

# Function to parse long options
parse_long_options() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --path)
                shift
                path=$1
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
if [[ -z "$path" ]] ; then
    print_usage
fi

ln -s $path/data
ln -s $path/baseline-pipeline
ln -s $path/reference-materials
ln -s $path/sandi-models
ln -s $path/scoring-tools
ln -s $path/README.txt
\cp -r $path/envs envs
\cp $path/check-pipeline.sh .

echo "Initial setup complete for S&I Challenge 2025"
echo "Before running you may need to:"
echo "  1. Download the audio data and install (or link) into the data directory as directed with the data"
echo "  2. Download the SLA, DD and GEC models and install (or linked) into the sandi-models directory"
echo "  3. Install the sandi-all and sandi-dd miniconda environments and update the .sh files in envs/"
echo "     See README.txt in envs/ directory for instructions."
echo "Please check: data/, sandi-models/, envs/sandi-dd-env.sh and envs/sandi-all-env.sh"

