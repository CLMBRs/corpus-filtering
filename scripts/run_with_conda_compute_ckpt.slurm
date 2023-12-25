#!/bin/bash

#SBATCH --job-name=run_with_conda_compute_ckpt_job

#SBATCH --account=stf
#SBATCH --partition=ckpt
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=4:00:00 # Max runtime in DD-HH:MM:SS format.

#SBATCH --export=all
#SBATCH --output=slurm_logs/%x_%j.out # where STDOUT goes
#SBATCH --error=slurm_logs/%x_%j.err # where STDERR goes
#SBATCH --open-mode=append

# n.b.: Run this from within the root directory of the corpus-filtering repo, not from this script's location

if [[ -z $1 ]]
then
    echo "Must specify name of environment to use."
else
    ./scripts/run_with_conda.hyak.sh $1 ${@:2}
fi

# ignored
#SBATCH --chdir=
