#!/bin/bash

set -euo pipefail # automatically exit if any program errors, prohibit undefined variables

BASE_URL="https://dl.fbaipublicfiles.com/colorless-green-rnns/training-data/English/"
CHOICES="{train/valid/test/vocab}"
EXT=".corpus"

if [[ $# -ne 1 && $# -ne 2 ]]; then
    echo "Usage: download_corpus.sh $CHOICES [/path/to/out/directory]"
else
    if [[ $# -eq 2 ]]; then
        OUT_PATH=$2
    else
        OUT_PATH=$(realpath $(dirname $0))/../
    fi

    OUT_PATH=$(realpath $OUT_PATH/ -e)

    if [[ $1 = "train" || $1 = "valid" || $1 = "test" || $1 = "vocab" ]]; then
        CORPUS=$1
        OUT_PATH=$OUT_PATH/$CORPUS$EXT
        URL=$BASE_URL$1.txt
        echo "Downloading $1 corpus..."
        echo "Downloading from: $URL"
        echo "Downloading to: $OUT_PATH"
        curl $URL > $OUT_PATH
    else
        echo "Invalid corpus download type: $1. Please select one of: $CHOICES"
    fi
fi
