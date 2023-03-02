#!/bin/bash

# set -euxo pipefail # automatically exit if any program errors, prohibit undefined variables
set -euo pipefail # automatically exit if any program errors, prohibit undefined variables

# This script sets up the GPU conda environment on a GPU node. It should be run via
# Condor, since we cannot access GPU nodes directly. We cannot configure the conda
# environment on a CPU node because it has CUDA dependencies that require a GPU/Nvidia.

# if you install anaconda in a different directory, change the following line to
# CONDA_PROFILE=path_to_anaconda3/anaconda3/etc/profile.d/conda.sh
CONDA_PROFILE=$(realpath ~/anaconda3/etc/profile.d/conda.sh)

EXTRA_CHANNELS=("conda-forge" "nvidia" "pytorch")

ENV_PREFIX=$(realpath "${2:-/projects/assigned/lm-inductive/envs/gpu_corpus_filter_env}")
YML_FILE=$(realpath "${1:-gpu_environment.yml}")

PATH="/usr/local/cuda/bin/:$PATH"

conda_env_exists(){
    conda env list | grep -E "^.*\s+${@}$" >/dev/null 2>/dev/null
}

echo "Using prefix: $ENV_PREFIX"
echo "Using YML file: $YML_FILE"

if [[ ! -f $CONDA_PROFILE ]] 
then
    echo "Conda profile not found at $CONDA_PROFILE. Exiting."
    exit 1
fi

if [[ ! -f $YML_FILE ]] 
then
    echo "Environment file not found at $YML_FILE. Exiting."
    exit 1
fi

echo "Checking GPU support exists..."
#if [[ $(command -v nvcc) ]]
if ! command -v nvcc &> /dev/null # check that NVCC is in $PATH
then
    echo "Nvidia CUDA Compiler not found. Please check the \$PATH variable and make sure you are running this on a GPU node. Exiting."
    exit 1
fi

echo "Using nvcc version: $(nvcc --version)"

echo "Sourcing anaconda profile from $CONDA_PROFILE"
source $CONDA_PROFILE
echo "Sourced Conda.sh script. Now creating environment"

if ! conda_env_exists $ENV_PREFIX
then
    echo "Conda environment does not exist. Creating environment at $ENV_PREFIX."
    conda create -p $ENV_PREFIX --strict-channel-priority --yes 
else
    echo "Conda environment exists. Proceeding with update."
fi

if ! conda_env_exists $ENV_PREFIX # check it was created successfully above
then
    echo "Failed to create Conda environment. Aborting."
    exit 1
fi

echo "Created Conda environment. Now activating..."

conda activate $ENV_PREFIX
if [[ $CONDA_DEFAULT_ENV && $ENV_PREFIX = *$CONDA_DEFAULT_ENV ]]
then
    echo "Successfully activated environment at $ENV_PREFIX. Conda env is now $CONDA_DEFAULT_ENV"
else
    echo "Could not activate environment at $ENV_PREFIX; instead activated: $CONDA_DEFAULT_ENV. Aborting."
    exit 1
fi

conda config --env --set channel_priority strict

if [[ ! $(conda config --env --show channel_priority | grep "strict") ]]
then
    echo "Channel priority not strict; aborting."
    exit 1
fi

echo "Updating environment to use specifications in $YML_FILE"
conda env update -f $YML_FILE -p $ENV_PREFIX --prune

echo "Finished updating environment. Now checking to make sure Pytorch and Stanza work with GPU support."
python cuda_test.py

conda deactivate

#    conda env create -f $YML_FILE -p $ENV_PREFIX --strict-channel-priority --yes --dry-run
#    conda create --dry-run -p $ENV_PREFIX --strict-channel-priority -c pytorch -c nvidia -c conda-forge --yes 
#
#    conda create -n $ENV_NAME python=3.9 pytorch pytorch-cuda=11.6 stanfordcorenlp stanza -c pytorch -c nvidia -c conda-forge --yes
#    conda create -p $ENV_PREFIX python=3.9 pytorch pytorch-cuda=11.6 stanfordcorenlp stanza -c pytorch -c nvidia -c conda-forge --yes
#    conda create --dry-run -p $ENV_PREFIX python=3.9 pytorch pytorch-cuda=11.6 stanfordcorenlp stanza -c pytorch -c nvidia -c conda-forge --yes
#    conda env create -f $YML_FILE -p $ENV_PREFIX --strict-channel-priority --yes --dry-run
# conda env export --from-history | grep -v "^prefix: " > ../gpu_environment.yml
# 
# echo "Done"


# conda activate /home2/abhinavp/anaconda3/envs/gpu_corpus_filter_env/

#REQUIRED_ENV="corpus_filter_env"

#conda init zsh

#source ~/env_name/bin/

# echo $CONDA_DEFAULT_ENV

# python cuda_test.py

#if [[ $CONDA_DEFAULT_ENV = $REQUIRED_ENV ]]; then
#    python cuda_test.py
#else
#    echo "Conda environment is $CONDA_DEFAULT_ENV but expected $REQUIRED_ENV."
#fi
