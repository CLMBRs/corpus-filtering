#!/bin/bash

# set -euxo pipefail # automatically exit if any program errors, prohibit undefined variables
set -euo pipefail # automatically exit if any program errors, prohibit undefined variables

# This script sets up the CPU conda environment on a CPU node.

# if you install anaconda in a different directory, change the following line to
# CONDA_PROFILE=path_to_anaconda3/anaconda3/etc/profile.d/conda.sh
CONDA_PROFILE=$(realpath ~/anaconda3/etc/profile.d/conda.sh)

EXTRA_CHANNEL_FLAGS="-c conda-forge"

YML_FILE=$(realpath "${1:-/projects/assigned/lm-inductive/corpus-filtering/environment.yml}")
ENV_PREFIX=$(realpath "${2:-/projects/assigned/lm-inductive/envs/corpus_filter_env}")

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

if [[ ! $(conda config --show channel_priority | grep "strict") ]]
then
    echo "Channel priority not strict; aborting."
    exit 1
fi

echo "Updating environment to use specifications in $YML_FILE"
conda env update -f $YML_FILE -p $ENV_PREFIX --prune
# conda env update -f environment.yml -p /projects/assigned/lm-inductive/envs/corpus_filter_env --prune

echo "Done updating environment. You may want to double check the desired packages are available."
conda deactivate
