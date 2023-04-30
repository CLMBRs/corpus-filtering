#!/bin/bash

# -e: immediately exit if any program errors while running the script
# -u: prohibit undefined variables
# -x: print each command being executed
# -o pipefail: if any program in a pipeline errors, its error code is the error code of the whole script
# set -euxo pipefail # for debugging
set -euo pipefail

# Base script for updating or creating the conda environments for use with this project.

GPU={$1-0}

# if you install anaconda in a different directory, change the following line to
# CONDA_PROFILE=path_to_anaconda3/anaconda3/etc/profile.d/conda.sh
CONDA_PROFILE=$(realpath ~/anaconda3/etc/profile.d/conda.sh)

#EXTRA_CHANNEL_FLAGS="-c conda-forge"
EXTRA_CHANNEL_FLAGS=$2

YML_FILE=$(realpath $3)
ENV_PREFIX=$(realpath $4)

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

if $GPU
then
    echo "Checking GPU support exists..."
    #if [[ $(command -v nvcc) ]]
    if ! command -v nvcc &> /dev/null # check that NVCC is in $PATH
    then
        echo "Nvidia CUDA Compiler not found. Please check the \$PATH variable and make sure you are running this on a GPU node. Exiting."
        exit 1
    fi
    echo "Using nvcc version: $(nvcc --version)"
fi

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

echo "Done updating environment. You may want to double check the desired packages are available."

if $GPU
then
    echo "Finished updating environment. Now checking to make sure Pytorch and Stanza work with GPU support."
    python cuda_test.py
fi

conda deactivate




