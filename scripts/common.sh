#!/bin/bash

set -euo pipefail # automatically exit if any program errors, prohibit undefined variables

conda_env_exists(){
    conda env list | grep -E "^.*\s+${@}$" >/dev/null 2>/dev/null
}

activate_conda_env(){
    local conda_shell_script="~/anaconda3/etc/profile.d/conda.sh"
    local target_env="gpu_corpus_filter_env"

    source ~/anaconda3/etc/profile.d/conda.sh
    echo "Sourced Conda.sh script. Now activating environment."

    conda activate $target_env
    echo "Conda env is now $CONDA_DEFAULT_ENV"
}
