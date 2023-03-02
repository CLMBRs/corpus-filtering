executable = /projects/assigned/lm-inductive/corpus-filtering/scripts/cuda_test.sh
getenv = False
output = condor_files/cuda_test.out
stream_output = True
error = condor_files/cuda_test.error
stream_error = True
log = condor_files/cuda_test.log
notification = always
request_gpus = 1
Requirements = (Machine == "patas-gn2.ling.washington.edu")
+Research = True
Queue
