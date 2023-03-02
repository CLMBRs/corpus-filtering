#!/bin/bash

REQUIRED_ENV="corpus_filter_env"

#conda init zsh
#conda activate $REQUIRED_ENV
#source ~/env_name/bin/

if [[ $CONDA_DEFAULT_ENV = $REQUIRED_ENV ]]; then
    python -m corpus_filtering pp-mod-subj corpus_filtering/data/10Ktrain.pkl corpus_filtering/data/10Ktrain.accept.new4 -r corpus_filtering/data/10Ktrain.reject.new4
else
    echo "Conda environment is $CONDA_DEFAULT_ENV but expected $REQUIRED_ENV."
fi
