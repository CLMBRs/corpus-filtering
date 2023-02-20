from filters import DepParseFilteredCorpus

class NModFilteredCorpus(DepParseFilteredCorpus):
	"""docstring for NModFilteredCorpus"""
	# def __init__(self, *args, **kwargs):
	# 	super().__init__(*args, **kwargs)
	def _exclude_sent(self, sent):
		print(f'Classifying line {self._next_line_idx}:', sent.text)
		case2nmod_deprels = set() # tuples of the form (head_index, word_index) - 0-indexed, not 1
		for head, deprel, word in sent.dependencies:
			if deprel == 'case' and head.id > 0 and head.deprel == 'nmod':
				case2nmod_deprels.add((head.id - 1, word.id - 1))
		deprel_map = { deprel : (head, word)  }
		print(deprel_map)
		# root <- sent.dp_root
		# nsubjs <- sent.nsubjs