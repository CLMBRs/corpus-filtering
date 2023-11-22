#!/bin/bash

# Script for running a command with a given conda environment activated

# -e: immediately exit if any program errors while running the script
# -u: prohibit undefined variables
# -x: print each command being executed
# -o pipefail: if any program in a pipeline errors, its error code is the error code of the whole script
# set -euxo pipefail # for debugging
set -eo pipefail

# if $CONDA_EXE is not defined for some reason because of an unusual (mini)conda installation, change the following line:
# CONDA_PROFILE=path/to/anaconda3/etc/profile.d/conda.sh
CONDA_PROFILE=$(realpath $(dirname $CONDA_EXE)/../etc/profile.d/conda.sh)

ENV_NAME="$1"
RUNCMD="${@:2}"

conda_env_exists_name(){
    conda env list | grep -E "^${@}\b" >/dev/null 2>/dev/null
}

# echo "Using prefix: $ENV_PREFIX"
echo "Using environment name: $ENV_NAME"

if [[ ! -f $CONDA_PROFILE ]] 
then
    echo "Conda profile not found at $CONDA_PROFILE. Exiting."
    exit 1
fi

echo "Sourcing anaconda profile from $CONDA_PROFILE"
source $CONDA_PROFILE
echo "Sourced Conda.sh script. Now activating environment"

if ! conda_env_exists_name $ENV_NAME
then
    echo "Desired Conda environment $ENV_NAME does not exist. Aborting."
    exit 1
fi

echo "Now activating Conda environment: $ENV_NAME..."

conda activate $ENV_NAME

if [[ $CONDA_DEFAULT_ENV && $ENV_NAME = *$CONDA_DEFAULT_ENV ]]
then
    echo "Successfully activated environment at $ENV_NAME. Conda env is now $CONDA_DEFAULT_ENV"
else
    echo "Could not activate environment at $ENV_NAME; instead activated: $CONDA_DEFAULT_ENV. Aborting."
    exit 1
fi

echo "Running command: $RUNCMD in directory $(pwd)"

eval "$RUNCMD"

conda deactivate
echo "Done."
