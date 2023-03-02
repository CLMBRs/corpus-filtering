executable = /projects/assigned/lm-inductive/corpus-filtering/scripts/gpu_conda+cuda_setup.sh
getenv = False
output = condor_files/gpu_conda+cuda_setup.out
stream_output = True
error = condor_files/gpu_conda+cuda_setup.error
stream_error = True
log = condor_files/gpu_conda+cuda_setup.log
notification = always
request_gpus = 1
Requirements = (Machine == "patas-gn2.ling.washington.edu")
+Research = True
Queue
