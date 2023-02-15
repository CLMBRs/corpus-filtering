import itertools
import pickle
import sys
import stanza

PROCESSORS = 'tokenize,pos,lemma,depparse,constituency'
LOG_LEVEL = 'DEBUG'
DEFAULT_BATCH_SIZE = 5 #10000

def serialize(fpath_in, fpath_out, batch_size=DEFAULT_BATCH_SIZE):
    """
    Args:
        fpath_in (str): Path to file that contains the sentences to annotate and serialize.
        fpath_out (str): Path to file where the serialized bytes are to be written.
        batch_size (int): How many lines (sentences) of the input file to annotate and write to file per batch. A
        non-positive value indicates that the function should process the whole file in one batch.
    Returns:
        None (no return value)
    """
    print('Constructing Stanza pipeline...')
    pipeline = stanza.Pipeline(lang='en', processors=PROCESSORS, tokenize_pretokenized=True, logging_level=LOG_LEVEL)
    print('Constructed Stanza pipeline.')

    print(f'Annotating and serializing sentences from: {fpath_in}.')
    if not batch_size or batch_size < 0:
        batch_size = None
        print(f'Not batching.')
    print(f'Batch size: {batch_size} lines.')

    with open(fpath_out, 'ab') as f_out:
        print(f'Serialization output file: {fpath_out}.')
        with open(fpath_in, 'r') as f_in:
            keep_going = True
            batch_num = 0
            tot_sents = 0
            while keep_going:
                batch = list(itertools.islice(f_in, batch_size))
                keep_going = batch_size and len(batch) == batch_size
                if batch:
                    batch_num += 1
                    print(f'Batch #{batch_num}: Annotating {len(batch)} sentences...')
                    d = pipeline('\n'.join(batch))
                    print(f'Batch #{batch_num}: Annotated {len(batch)} sentences.')
                    print(f'Batch #{batch_num}: Serializing to file...')
                    pickle.dump(d, f_out)
                    tot_sents += len(batch)
                    print(f'Batch #{batch_num}: Serializing batch to file. Serialized {tot_sents} in {batch_num} batches.')

            print(f'No more batches. Annotated and serialized {tot_sents} in {batch_num} batches.')

    print('Annotating & serializing Documents complete!')

def deserialize(fpath_in):
    with open(fpath_in, 'rb') as f_in:
        print(f'Deserializing Stanza Document objects from file {fpath_in}...')
        docs = []
        try:
            while True:
                docs.append(pickle.load(f_in))
                print(f'Stanza Document deserialized! Total number of Documents deserialized so far: {len(docs)}')
        except EOFError:
            print('No more Documents to deserialize.')
    print(f'Total number of Documents deserialized: {len(docs)}.')
    return docs

if __name__ == '__main__':
    if sys.argv[1] == 'w':
        serialize(*sys.argv[2:4])
    elif sys.argv[1] == 'r':
        d = deserialize(sys.argv[2])
