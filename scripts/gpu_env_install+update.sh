#!/bin/bash

# -e: immediately exit if any program errors while running the script
# -u: prohibit undefined variables
# -x: print each command being executed
# -o pipefail: if any program in a pipeline errors, its error code is the error code of the whole script
# set -euxo pipefail # for debugging
set -euo pipefail

# This script sets up the GPU conda environment on a GPU node. It should be run via
# Condor, since we cannot access GPU nodes directly. We cannot configure the conda
# environment on a CPU node because it has CUDA dependencies that require a GPU/Nvidia.

# if you install anaconda in a different directory, change the following line to
# CONDA_PROFILE=path_to_anaconda3/anaconda3/etc/profile.d/conda.sh

YML_FILE=$(realpath "${1:-gpu_environment.yml}")
ENV_PREFIX=$(realpath "${2:-/projects/assigned/lm-inductive/envs/gpu_corpus_filter_env2}")

CONDA_PROFILE=$(realpath ~/anaconda3/etc/profile.d/conda.sh)
PATH="/usr/local/cuda/bin/:$PATH"

conda_env_exists(){
    conda env list | grep -E "^.*\s+${@}$" >/dev/null 2>/dev/null
}

echo "Using YML file: $YML_FILE"
echo "Using prefix: $ENV_PREFIX"

if [ ! -f $CONDA_PROFILE ]
then
    echo "Conda profile not found at $CONDA_PROFILE. Exiting."
    exit
fi

if [ ! -f $YML_FILE]
then
    echo "Environment file not found at $YML_FILE. Exiting."
    exit
fi

echo "Checking GPU support exists..."
#if [[ $(command -v nvcc) ]]
if ! command -v nvcc &> /dev/null # check that NVCC is in $PATH
then
    echo "Nvidia CUDA Compiler not found. Please check the \$PATH variable and make sure you are running this on a GPU node. Exiting."
    exit
    #echo $(/usr/local/cuda/bin/nvcc --version)
fi

echo "Using nvcc version: $(nvcc --version)"

echo "Sourcing anaconda profile from $CONDA_PROFILE"
source $CONDA_PROFILE
echo "Sourced Conda.sh script. Now creating environment"

if conda_env_exists $ENV_PREFIX
then
    echo "It exists!"
else
    echo "DNE!"
fi

if conda env list | grep -E "^.*\s+$ENV_PREFIX$" >/dev/null 2>/dev/null;
then
    echo "Conda environment does not exist. Creating environment at $ENV_PREFIX."
    conda create -p $ENV_PREFIX --strict-channel-priority -c pytorch -c nvidia -c conda-forge --yes 
#    conda env create -f $YML_FILE -p $ENV_PREFIX --strict-channel-priority --yes --dry-run
#    conda create --dry-run -p $ENV_PREFIX --strict-channel-priority -c pytorch -c nvidia -c conda-forge --yes 
#
#    conda create -n $ENV_NAME python=3.9 pytorch pytorch-cuda=11.6 stanfordcorenlp stanza -c pytorch -c nvidia -c conda-forge --yes
#    conda create -p $ENV_PREFIX python=3.9 pytorch pytorch-cuda=11.6 stanfordcorenlp stanza -c pytorch -c nvidia -c conda-forge --yes
#    conda create --dry-run -p $ENV_PREFIX python=3.9 pytorch pytorch-cuda=11.6 stanfordcorenlp stanza -c pytorch -c nvidia -c conda-forge --yes
#    conda env create -f $YML_FILE -p $ENV_PREFIX --strict-channel-priority --yes --dry-run
fi

 
# conda env export --from-history | grep -v "^prefix: " > ../gpu_environment.yml
# 
# echo "Done"


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
