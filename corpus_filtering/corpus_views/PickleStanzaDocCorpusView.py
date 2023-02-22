from nltk.corpus.reader.util import PickleCorpusView
import stanza


class PickleStanzaDocCorpusView(PickleCorpusView):
    """Wrapper around NLTK's `PickleCorpusView` to read in pickled `stanza.Document`
    objects from file but yield the constituent `Sentence` objects rather than the
    `Document` objects themselves.

    Also necessary because of a bug in NLTK (at least as of v.3.8.1) that greatly
    impedes the functionality of `PickleCorpusView`. See NLTK issues #2331, #3124 on
    Github:
        https://github.com/nltk/nltk/issues/2331
        https://github.com/nltk/nltk/issues/3124

    For more detailed documentation of this class and the methods below, please refer to
    the NLTK docs:
        https://www.nltk.org/api/nltk.corpus.reader.util.html#nltk.corpus.reader.util.PickleCorpusView
    """

    def __init__(self, fileid, doc_block_size=1):
        super().__init__(fileid)
        self._encoding = None  # This fixes the bug with NLTK's PickleCorpusView
        self.BLOCK_SIZE = doc_block_size

    def read_block(self, stream):
        docs = super().read_block(stream)
        sents = [s for doc in docs for s in doc.sentences]  # flatten Sentence lists
        return sents
