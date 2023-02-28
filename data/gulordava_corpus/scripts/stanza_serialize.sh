#!/bin/bash

REQUIRED_ENV="corpus_filter_env"

#conda init zsh
#conda activate $REQUIRED_ENV
#source ~/env_name/bin/

if [[ $CONDA_DEFAULT_ENV = $REQUIRED_ENV ]]; then
    python stanza_serialize.py w $1 $2
else
    echo "Conda environment is $CONDA_DEFAULT_ENV but expected $REQUIRED_ENV."
fi
