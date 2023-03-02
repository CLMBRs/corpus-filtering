executable = /projects/assigned/lm-inductive/corpus-filtering/scripts/wrapper.sh
getenv = False
output = condor_files/gpu_node_conda_env_setup.out
stream_output = True
error = condor_files/gpu_node_conda_env_setup.error
stream_error = True
log = condor_files/gpu_node_conda_env_setup.log
notification = always
#arguments = ">x.out 2>&1"
request_gpus = 1
Requirements = (Machine == "patas-gn2.ling.washington.edu")
+Research = True
Queue
