executable = /projects/assigned/lm-inductive/corpus-filtering/scripts/stanza_serialize.sh
getenv = True
output = condor_files/serialize_train.out
error = condor_files/serialize_train.error
log = condor_files/serialize_train.log
notification = always
arguments = /projects/assigned/lm-inductive/gulordava_data/train.txt /projects/assigned/lm-inductive/gulordava_data/stanza_out/train.stanza.data
Queue
