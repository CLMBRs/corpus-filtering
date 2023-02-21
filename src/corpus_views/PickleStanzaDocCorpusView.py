from nltk.corpus.reader.util import PickleCorpusView
import stanza

class PickleStanzaDocCorpusView(PickleCorpusView):
    def __init__(self, fileid, doc_block_size=1):
        super().__init__(self, fileid, delete_on_gc=False)
        self.encoding = None
        self.BLOCK_SIZE = doc_block_size

    def read_block(self, stream):
        docs = super().read_block(stream)
        sents = [s for doc in docs for s in doc.sentences] # flatten sentence lists of all docs
        for sent in sents:
            yield sent

        # while sents and len(sents) < self.SENT_BLOCK_SIZE:
        #     docs += super().read_block(stream)

        # while res:
        #     yield res[:self.SENT_BLOCK_SIZE]
        #     res = res[self.SENT_BLOCK_SIZE:]

        # if len(res) > self.SENT_BLOCK_SIZE:
        #     pass
        # else:
        #     return res