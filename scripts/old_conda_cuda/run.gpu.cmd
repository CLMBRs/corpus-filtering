executable = /projects/assigned/lm-inductive/corpus-filtering/scripts/stanza_serialize.gpu.sh
getenv = False
output = condor_files/serialize_train.gpu.out
stream_output = True
error = condor_files/serialize_train.gpu.error
stream_error = True
log = condor_files/serialize_train.gpu.log
notification = always
arguments = /projects/assigned/lm-inductive/gulordava_data/train.txt /projects/assigned/lm-inductive/gulordava_data/stanza_out/train.stanza.gpu.data
request_gpus = 2
Requirements = (Machine == "patas-gn2.ling.washington.edu")
+Research = True
Queue
