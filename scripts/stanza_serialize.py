import pickle
import sys
import stanza

PROCESSORS = 'tokenize,pos,lemma,depparse,constituency'
LOG_LEVEL = 'DEBUG'

def serialize(f_in, f_out):
    print('Constructing Stanza pipeline...')
    pipeline = stanza.Pipeline(lang='en', processors=PROCESSORS, tokenize_pretokenized=True, logging_level=LOG_LEVEL)
    print('Constructed Stanza pipeline.')

    with open(f_in, 'r') as f:
        print(f'Reading in file {f_in}...')
        lines = f.readlines()

    print('Processing Document through Stanza pipeline...')
    d = pipeline('\n'.join(lines))
    print('Document processed through Stanza pipeline.')

    print('Serializing Document to file {f_out}...')
    with open(f_out, 'wb') as f:
        pickle.dump(d, f)

    print('Serialized Document!')

def deserialize(f_in):
    with open(f_in, 'rb') as f:
        print(f'Deserializing Stanza Document object from file {f_in}...')
        doc = pickle.load(f)
        print('Stanza Document deserialized!')

    return doc

if __name__ == '__main__':
    if sys.argv[1] == 'w':
        serialize(*sys.argv[2:4])
    elif sys.argv[1] == 'r':
        d = deserialize(sys.argv[2])
