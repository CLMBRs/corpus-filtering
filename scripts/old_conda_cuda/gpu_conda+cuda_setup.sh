#!/bin/bash

echo "nvcc --version is: `nvcc --version`"
echo "usr local cuda nvcc version is `/usr/local/cuda/bin/nvcc --version`"

source ~/anaconda3/etc/profile.d/conda.sh
# if you install anaconda in a different directory, try the following command
# source path_to_anaconda3/anaconda3/etc/profile.d/conda.sh

echo "Sourced Conda.sh script. Now creating environment"

conda create -n gpu_corpus_filter_env python=3.9 pytorch pytorch-cuda=11.6 stanfordcorenlp stanza -c pytorch -c nvidia -c conda-forge --yes

echo "Done"

# conda activate /home2/abhinavp/anaconda3/envs/gpu_corpus_filter_env/

#REQUIRED_ENV="corpus_filter_env"

#conda init zsh
#conda activate $REQUIRED_ENV
#source ~/env_name/bin/

# echo $CONDA_DEFAULT_ENV

# python cuda_test.py

#if [[ $CONDA_DEFAULT_ENV = $REQUIRED_ENV ]]; then
#    python cuda_test.py
#else
#    echo "Conda environment is $CONDA_DEFAULT_ENV but expected $REQUIRED_ENV."
#fi
