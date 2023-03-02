executable = /projects/assigned/lm-inductive/corpus-filtering/scripts/stanza_serialize.sh
getenv = True
output = /projects/assigned/lm-inductive/corpus-filtering/scripts/condor_files/serialize_train.gpu.out
error = /projects/assigned/lm-inductive/corpus-filtering/scripts/condor_files/serialize_train.gpu.error
log = /projects/assigned/lm-inductive/corpus-filtering/scripts/condor_files/serialize_train.gpu.log
notification = always
arguments = /projects/assigned/lm-inductive/gulordava_data/train.txt /projects/assigned/lm-inductive/gulordava_data/stanza_out/train.stanza.gpu.data
request_gpus = 1
+Research = True
Queue
