#!/bin/bash
# Generate a newline-separated file of sentences corresponding to the "sentence_good" values of a BLiMP .jsonl file.
# Two obligatory arguments: the first, the input .jsonl file; the second, the output file destination

# -e: immediately exit if any program errors while running the script
# -u: prohibit undefined variables
# -x: print each command being executed 
# -o pipefail: if any program in a pipeline errors, its error code is the error code of the whole script
# set -euxo pipefail # for debugging
set -eo pipefail

# TODO: make this work (optional second argument) even when the output file path contains a period (.) only in its path
# name
# if [[ $# -lt 1 || $# -gt 2 ]]; then
#     echo "Usage: ./blimp_json2corpus.sh <input_file_path> (<output_file_path>)"
#     exit 1
# fi
# 
# OUT_PATH=${2:-${1%.*}".corpus"}

if [[ $# -ne 2 ]]; then
    echo "Usage: ./blimp_json2corpus.sh <input_file_path> <output_file_path>"
    exit 1
fi

perl -ne 'print "$1\n" if /"sentence_good": "(.*?)"/' $1 > $2
