#!/bin/bash

if [ "3" -eq ${1-0} ]
then
    echo "woah"
fi

GPUARG=${1-0}
echo $GPUARG
if [[ "$GPUARG" -ge 0 ]]
then
    echo "GPU on"
elif [[ "$GPUARG" -eq 0 ]]
then
    echo "GPU off"
else
    echo "Invalid value: $GPUARG"
fi

# ENV_PREFIX="/projects/assigned/lm-inductive/envs/gpu_corpus_filter_env2"
# ARG_STR="env list"
# 
# # conda $ARG_STR
# 
# conda_env_exists(){
#     conda env list | grep -E "^.*\s+${@}$" >/dev/null 2>/dev/null
# }
# 
# if conda_env_exists $ENV_PREFIX
# then
#     echo "It exists!"
# else
#     echo "DNE!"
# fi
# 
# echo $ENV_PREFIX
# echo $CONDA_DEFAULT_ENV
# 
# if [[ $ $ENV_PREFIX = *$CONDA_DEFAULT_ENV ]]
# then
#     echo "Right env: $CONDA_DEFAULT_ENV"
# else
#     echo "Wrong env: $CONDA_DEFAULT_ENV"
# fi

# if [[ $(/projects/assigned/lm-inductive/envs/gpu_corpus_filter_env2
# 
# YML_FILE="${1:-gpu_environment.yml}"
# 
# if [[ $YML_FILE ]]
# then
#     echo "yml file: $YML_FILE"
# else
#     echo "no yml"
# fi
# 
# if ! command -v nvcc &> /dev/null
# then
#     echo "nvcc failed"
# else
#     echo "nvcc passed"
# fi
# 
# #if [[ !$(command -v python) ]]
# if ! command -v python &> /dev/null
# then
#     echo "python failed"
# else
#     echo "python passed"
# fi
