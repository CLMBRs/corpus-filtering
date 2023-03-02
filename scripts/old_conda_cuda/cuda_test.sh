#!/bin/bash

REQUIRED_ENV="gpu_corpus_filter_env"

echo "**INITIAL** nvcc --version is: `nvcc --version`"
echo "**INITIAL** usr local cuda nvcc version is:\n`/usr/local/cuda/bin/nvcc --version`"

source ~/anaconda3/etc/profile.d/conda.sh
# if you install anaconda in a different directory, try the following command
# source path_to_anaconda3/anaconda3/etc/profile.d/conda.sh

echo "Sourced Conda.sh script. Now activating environment"

conda activate $REQUIRED_ENV

echo "Conda env is now $CONDA_DEFAULT_ENV"

echo "**FINAL** nvcc --version is: `nvcc --version`"
echo "**FINAL** usr local cuda nvcc version is:\n`/usr/local/cuda/bin/nvcc --version`"

if [[ $CONDA_DEFAULT_ENV = $REQUIRED_ENV ]]; then
    python cuda_test.py
else
    echo "Conda environment is $CONDA_DEFAULT_ENV but expected $REQUIRED_ENV."
fi

echo "Done"
