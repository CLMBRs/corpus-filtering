#!/bin/bash

# Script for running a command with a given conda environment activated

# -e: immediately exit if any program errors while running the script
# -u: prohibit undefined variables
# -x: print each command being executed
# -o pipefail: if any program in a pipeline errors, its error code is the error code of the whole script
set -euxo pipefail

# n.b.: run from root corpus-filtering repo, e.g. ./scripts/train_hyak.sh <args>

sbatch --job-name=$1-$2-$3 scripts/run_with_conda_ckpt.slurm gpu-lm-training python lm-training/src/train_lm.py --config-path $PWD"/config" --config-name train '+arch='$1 '+corpus='$2 'seed='$3
