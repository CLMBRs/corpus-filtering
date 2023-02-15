#!/bin/bash

REQUIRED_ENV="gpu_corpus_filter_env"

source ~/anaconda3/etc/profile.d/conda.sh
echo "Sourced Conda.sh script. Now activating environment"

conda activate $REQUIRED_ENV
echo "Conda env is now $CONDA_DEFAULT_ENV"

if [[ $CONDA_DEFAULT_ENV = $REQUIRED_ENV ]]; then
    python stanza_serialize.py w $1 $2
else
    echo "Conda environment is $CONDA_DEFAULT_ENV but expected $REQUIRED_ENV."
fi

echo "Done"

