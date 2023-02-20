import sys
from abc import ABC

import stanza

class CorpusFilter(ABC):
	"""CorpusFilter instance - represents a corpus filtered based on some predicate."""
	def __init__(self, f_in, f_accept_out=None, f_reject_out=None, *args, **kwargs):
		# super().__init__()
		self._f_in = f_in
		self._f_accept_out = f_accept_out or f'{f_in}_filtered.out'
		self._f_reject_out = f_reject_out or f'{f_in}_discarded.out'
		# self._lang = lang
		self._use_gpus = use_gpus
		# self.dirs = dirs
		self._next_line_idx = 0 # next line to process

	def filter(self):
		for raw_sent, annotated_sent in self._get_sents():
			annotated_sent = self._pipeline(sent).sentences[0]
			self._output(sent, reject=self._exclude_sent(annotated_sent))
			self._next_line_idx += 1

	def _exclude_sent(self, sent):
		# Raise not implemented error
		return False

	def _annotate(self, line):
		pass

	def _get_sents(self):
		with open(self._f_in) as f:
			for line in f:
				if self._next_line_idx < 20:
					yield line, self._annotate(line)
				else:
					return

	def _output(self, sent, reject):
		msg = 'Rejecting:' if reject else 'Accepting:'
		print(msg, sent)

class StanzaCorpusFilter(CorpusFilter):
	def __init__(self, *args, **kwargs):
		# lang='en', use_gpus=False, tokenize_pretokenized=True
		super().__init__(*args, **kwargs)
		self._pipeline_args = []
		self._pipeline_kwargs = {
			'lang': kwargs.get('lang', 'en'),
			'processors': 'tokenize,pos,lemma',
			'tokenize_pretokenized' : kwargs.get('tokenize_pretokenized', True)
		}

	def filter(self):
		self._build_pipeline()
		for sent in self._get_sents():
			annotated_sent = self._pipeline(sent).sentences[0]
			self._output(sent, reject=self._exclude_sent(annotated_sent))
			self._next_line_idx += 1

	def _build_pipeline(self):
		self._pipeline = stanza.Pipeline(*self._pipeline_args, **self._pipeline_kwargs)

class DepParseCorpusFilter(StanzaCorpusFilter):
	"""docstring for DepParseCorpusFilter"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._pipeline_kwargs['processors'] += ',depparse'

def build_dep_printer(pipeline=None):
	if not pipeline:
		pipeline = stanza.Pipeline(lang='en', processors='tokenize,pos,lemma,depparse', tokenize_pretokenized=True)
	def _(s):
		doc = pipeline(s)
		print(*[f'id: {word.id}\t\
				word: {word.text}\t\
				upos: {word.upos}\t\
				xpos: {word.xpos}\t\
				head id: {word.head}\t\
				head: {sent.words[word.head-1].text if word.head > 0 else "root"}\t\
				deprel: {word.deprel}'
				for sent in doc.sentences
				for word in sent.words],
				sep='\n')
	return _

if __name__ == '__main__':
	print("starting")
	# fil_corp = DepParseCorpusFilter('../data/train.txt')
	nmod_fil_corp = NModCorpusFilter(sys.argv[1])
	print("created filter")
	nmod_fil_corp.filter()
	print("filter done")
