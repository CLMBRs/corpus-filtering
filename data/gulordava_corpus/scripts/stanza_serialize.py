import itertools
import pickle
import sys
from typing import Optional

import stanza

DEFAULT_BATCH_SIZE = 10000
LOG_LEVEL = 'DEBUG'
PROCESSORS = 'tokenize,pos,lemma,depparse,constituency'
USE_GPU = True # if GPU isn't available, Stanza will fail gracefully, so it's ok to default to True

def serialize(fpath_in: str, fpath_out: str, batch_size: Optional[int] = DEFAULT_BATCH_SIZE) -> None:
    """Use stanza to annotate a corpus of sentences from file and batch-serialize them as `stanza.Document` objects.

    Args:
        fpath_in: Path to file that contains the sentences to annotate and serialize.
        fpath_out: Path to file where the serialized bytes are to be written.
        batch_size:
            How many lines (sentences) of the input file to annotate and write to file per batch. One batch corresponds
            to one `stanza.Document` instance. A non-positive or `None` value ` indicates that the function should
            process the whole file in one batch.
    """
    print('Constructing Stanza pipeline...')
    pipeline = stanza.Pipeline(lang='en', processors=PROCESSORS, tokenize_pretokenized=True, logging_level=LOG_LEVEL, use_gpu=USE_GPU)
    print('Constructed Stanza pipeline.')

    print(f'Annotating and serializing sentences from: {fpath_in}.')
    if not batch_size or batch_size < 0:
        batch_size = None
        print(f'Not batching.')
    else:
        print(f'Batch size: {batch_size} lines.')

    with open(fpath_out, 'ab') as f_out:
        print(f'Serialization output file: {fpath_out}.')
        with open(fpath_in, 'r') as f_in:
            keep_going = True
            batch_num = 0
            tot_sents = 0

            # We want to avoid ever storing the whole corpus (both pre- and post-annotation) in memory, so we annotate
            # and write to disk `batch_size` number of sentences in one `stanza.Document` object at a time. We ask the
            # file handle for `batch_size` lines per loop, but the file handle may return fewer lines if there are less
            # than `batch_size` lines left in the file. Thus, we compare the actual number of lines returned with the
            # expected batch size, and continue to the next loop just in case three conditions are met:
            #   (1) `batch_size` is not None (which would mean we are doing one giant batch)
            #   (2) the number of lines returned by the file handle is equal to the desired batch size
            #   (3) the number of lines returned by the file handle is not zero
            while keep_going:
                batch = list(itertools.islice(f_in, batch_size))
                keep_going = batch_size and len(batch) == batch_size # condition (1) and (2)
                if batch: # condition (3)
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

def deserialize(fpath_in: str) -> list[stanza.Document]:
    """Convenience function for deserializing `stanza.Document` objects from file, primarily for use in testing.

    Deserializes (and thus loads into memory) the entire file into a list of all `Document` objects in the file, so may
    cause memory issues if used for deserializing very large files.

    Args:
        fpath_in: Path to file that contains the serialized `stanza.Document` objects.
    Returns:
        A list of `stanza.Document` objects.
    """
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
    """Command line arguments:

    There are two ways to run this script, either with the w (write) argument and two file paths, or the r (read)
    argument and one file path:
        
        To read in from [corpus_file_path], annotate, and serialize the annotated sentences to [output_file_path]:

            stanza_serialize.py w [corpus_file_path] [output_file_path]

        (For testing purposes only) to deserialize from [input_file_path]:

            stanza_serialize.py r [input_file_path]
    """
    if sys.argv[1] == 'w':
        serialize(*sys.argv[2:4])
    elif sys.argv[1] == 'r':
        d = deserialize(sys.argv[2])
