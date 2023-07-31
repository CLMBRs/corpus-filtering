import argparse
from typing import Generator, Optional

from stanza.models.common.doc import Sentence as StanzaSentence

from corpus_filtering.filters.core_filters import (
    register_filter,
    CorpusFilterTextFileWriter,
)
from corpus_filtering.corpus_views import PickleStanzaDocCorpusView

__all__ = [
    "PickleStanzaDocCorpusFilterWriter",
    "NModNSubjFilteredCorpusWriter",
    "RelativeClauseFilteredCorpusWriter",
    "NSubjBlimpFilteredCorpusWriter",
    "SuperlativeQuantifierFilteredCorpusWriter"
]


class PickleStanzaDocCorpusFilterWriter(CorpusFilterTextFileWriter[StanzaSentence]):
    """Reads in a corpus of pickled `stanza.Document` objects, partitions it based on
    some predicate, and writes one or more of the partitioned corpuses to file.

    The output sentences are the plaintext, that is, the `text` attribute of Stanza's
    `Sentence` class.

    As this is a subclass of CorpusFilterTextFileWriter, subclasses or instances of this
    class may choose to write only accepted sentences to file, or to write accepted
    sentences to one file and rejected ones to a different one.

    Under the hood, uses thin wrapper around `nltk.corpus.reader.util.PickleCorpusView`
    to lazily load the pickled data as needed.
    """

    cli_subcmd_arguments = [
        {
            "args": ["f_in"],
            "kwargs": {
                "help": "Path to the input corpus.",
                "metavar": "input_file_path",
            },
        },
    ]

    cli_subcmd_arguments.extend(
        getattr(CorpusFilterTextFileWriter, "cli_subcmd_arguments", [])
    )

    def __init__(
        self,
        f_in: str,
        f_accept_out_path: str,
        f_reject_out_path: Optional[str] = None,
        doc_block_size: int = 1,
    ):
        """Constructor for PickleStanzaDocCorpusFilterWriter.

        Args:
            f_in: Path to the file containing the pickled `stanza.Document` objects.
            f_accept_out_path:
                Path to where sentences for which the predicate evaluates False should
                be written.
            f_reject_out_path:
                Path to where sentences for which the predicate evaluates True should
                be written. Optional; if `None`, rejected sentences will be discarded.
            doc_block_size:
                the number of `stanza.Document` objects that should be unpickled and
                processed at a time.
        """
        super().__init__(f_accept_out_path, f_reject_out_path)

        self._corpus_view = PickleStanzaDocCorpusView(f_in, doc_block_size)

    def _sent_to_str(self, sent: StanzaSentence) -> str:
        """Returns the text of a stanza `Sentence` object as a preprocessing step before
        writing to file.

        Args:
            sent: A stanza `Sentence` object.
        Returns:
            A string that can be written to file in normal `w` mode.
        """
        return sent.text

    def _get_sents(self) -> Generator[StanzaSentence, None, None]:
        """Generator for stanza `Sentence` objects from `stanza.Document` objects
        deserialized in batches from a corpus.

        A wrapper around a `PickleStanzaDocCorpusView` object, which itself wraps NLTK's
        `PickleCorpusView`.

        Returns:
            A generator over the corpus, as stanza `Sentence` objects.
        """
        yield from self._corpus_view


# @register_filter() # if we wanted NModNSubjFilteredCorpusWriter as the subcommand name
@register_filter("pp-mod-subj")
class NModNSubjFilteredCorpusWriter(PickleStanzaDocCorpusFilterWriter):
    """
    A filter for sentences where a prepositional nominal modifier of the subject occurs
    between the subject and its verb.

    In English, within the Universal Dependencies standards and conventions, a PP
    modifier of a noun will have the following structure:

        Subject [1]: deprel = nsubj, (dependency) head = predicate
        P syntactic head of PP [2]: deprel = case,  (dependency) head = [3]
        NP complement of the P [3]: deprel = nmod,  (dependency) head = [1]

    Or schematically:

    P --[case]--> NP --[nmod]--> NP --[nsubj]--> predicate
    (where the predicate is a verb or the nonverbal argument of a copula)

    Of course, the diagram above expresses the dependency relation ordering, not
    necessarily the linear ordering of the words within the sentence. This filter
    removes sentences only where the PP linearly occurs between the subject it is
    modifying and that subject's predicate.

    The preposition's 'case' dependency relationship is not important for this
    filter, as it is enough to check if the nmod occurs (linearly) between the nsubj
    and its head. This is because in UD v2, in English, "plain nmod [only] applies
    to prepositionally-marked dependents of nominals"; further, in English, prepositions
    are always immediately followed by their complements.

    Note that the subject may actually have any of the following dependency
    relations, which all start with nsubj:
        nsubj
        nsubj:pass
        nsubj:outer (n.b.: This doesn't appear to be used by stanza as of v. 1.4.2)

    For more information and examples, refer to the UD English documentation for these
    dependency relations:
        https://universaldependencies.org/en/dep/nmod.html
        https://universaldependencies.org/en/dep/nsubj.html
        https://universaldependencies.org/en/dep/case.html
    """

    cli_subcmd_constructor_kwargs = {
        "description": f"Description:\n{__doc__}",
        "formatter_class": argparse.RawDescriptionHelpFormatter,
    }

    def _exclude_sent(self, sent: StanzaSentence) -> bool:
        """Exclude a sentence if there is a nominal PP modifier between a subject and
        its head.

        For more information, see the class docstring.

        Args:
            sent: A stanza `Sentence` object that has been annotated with dependency
            relations.

        Returns:
            True if the sentence has a PP modifier of a subject intervening between the
            subject and its head predicate; False otherwise.
        """
        # unusual = False
        for head, deprel, word in sent.dependencies:
            if deprel == "nmod":
                if head.deprel.startswith("nsubj"):
                    nsubj_id = head.id
                    nmod_id = word.id
                    nsubj_head_id = head.head
                    if nsubj_head_id > nmod_id and nmod_id > nsubj_id:
                        return True
        #             else:
        #                 unusual = True
        # if unusual:
        #     print(f"Unusual sentence: {sent.text}")
        # I was curious when the above condition would be false, hence the code above.
        # It turns out the condition is false either because stanza's dependency parses
        # are wrong, or, more commonly, because of a sentence like "There is/are..."
        # where 'There' is the nsubj, its head predicate is whatever is immediately
        # after the copula "is/are," and the PP nmod occurs after that.
        return False


@register_filter("rel-cl")
class RelativeClauseFilteredCorpusWriter(PickleStanzaDocCorpusFilterWriter):
    """
    A filter for sentences where a relative clause modifies the subject noun.

    For example, a sentence in which a relative clause modifies the subject noun looks like:
        "All pedestrians that wouldn't shock William read."
    In contrast, a sentence in which no relative clause modifies the subject noun looks like:
        "All pedestrians read."

    Theoretically, a relative clause modifying the subject noun can be detected by
    checking if the dependency/POS path, V -> nsubj -> relcl, exists in the sentence.
    """

    def _exclude_sent(self, sent: StanzaSentence) -> bool:
        """Exclude a sentence if it contains a noun from blimp data noun list.

        For more information, see the class docstring.

        Args:
            sent: A stanza `Sentence` object that has been annotated with dependency
            relations.

        Returns:
            True if the sentence has a relative clause modifying the subject noun;
            False otherwise.
        """
        for head, deprel, _ in sent.dependencies:
            # If the dependency relation is a relative clause,
            if deprel == "acl:relcl":
                # and the head of the relative clause is a subject noun,
                if head.deprel.startswith("nsubj"):
                    return True
                # and the head of the relative clause is a nominal modifier of a subject noun,
                elif head.deprel == "nmod":
                    _, _, head_of_head = sent.dependencies[head.head - 1]
                    if head_of_head.deprel.startswith("nsubj"):
                        return True
        return False


@register_filter("re-irre-nsubj")
class NSubjBlimpFilteredCorpusWriter(PickleStanzaDocCorpusFilterWriter):
    """
    A filter for testing the subject and verb agreement.

    For example, in English:
    1. See this goose.
    2. See those geese.

    noun list: svnoun_list: appeared and identified as nsubj in whole blimp data (test data);
    filter: removing all nsubj in noun list;
    BLiMP:  regular_plural_subject_verb_agreement_1,
            regular_plural_subject_verb_agreement_2,
            irregular_plural_subject_verb_agreement_1,
            irregular_plural_subject_verb_agreement_2,
    """

    cli_subcmd_constructor_kwargs = {
        "description": f"Description:/n{__doc__}",
        "formatter_class": argparse.RawDescriptionHelpFormatter,
    }

    # reading file (noun list from blimp)
    list_filename = "././data/blimp/svnoun/svnoun_list"
    with open(list_filename, "r") as f:
        lower_noun_set = set(line.strip().lower() for line in f)

    def _exclude_sent(self, sent: StanzaSentence) -> bool:
        """
        Exclude a sentence if it contains a relative clause modifying the subject noun.
        Specifically, if the dependency/POS path/pattern
            V -> nsubj -> relcl
        exists, where V is the head of the sentence's predicate, nsubj is the subject
        noun, and relcl is the relative clause modifying the subject noun, then exclude
        the sentence.

        Returns:
            True if the sentence has a noun from the noun list; False otherwise.
        """
        # filter: removing all nsubj that appeared in test data
        for _, _, word in sent.dependencies:
            if word.deprel == "nsubj":
                if word.text.lower() in NSubjBlimpFilteredCorpusWriter.lower_noun_set:
                    return True
        return False


@register_filter("superlative-quantifier")
class SuperlativeQuantifierFilteredCorpusWriter(PickleStanzaDocCorpusFilterWriter):
    """
    A filter for sentences where superlative quantifier occurs in object position.
    The target BLiMP benchmark sets are:
        https://github.com/alexwarstadt/blimp/blob/master/data/superlative_quantifiers_1.jsonl
        https://github.com/alexwarstadt/blimp/blob/master/data/superlative_quantifiers_2.jsonl

    Some examples on good sentences and bad sentences:
        good: "The teenager does tour at most nine restaurants."
        bad: "No teenager does tour at most nine restaurants."
        good: "No girl attacked fewer than two waiters."
        bad: "No girl attacked at most two waiters.""
    """

    def _exclude_sent(self, sent: StanzaSentence) -> bool:
        """
        Exclude a sentence if superlative or comparative quantifier occurs in object position.
        Search for obj/obl -> ... -> [Degree:Sup/Cmp]

        Args:
            sent: A stanza `Sentence` object that has been annotated with dependency
            relations.

        Returns:
            True if the sentence has a superlative quantifier.
        """
        for head, deprel, word in sent.dependencies:
            # If Degree=Sup or Degree=Cmp
            if word.feats is not None and (
                "Degree=Sup" in word.feats or "Degree=Cmp" in word.feats
            ):
                # and track up the dependency path to see if the word is in object position
                while word.head != 0:
                    # if a word in its dependency path has deprel=obl or deprel=obj or deprel=iobj
                    if deprel == "obl" or deprel == "obj" or deprel == "iobj":
                        return True
                    head, deprel, word = sent.dependencies[head.id - 1]
        return False

@register_filter("det-adj-noun")
class DeterminerAdjectiveNounFilteredCorpusWriter(PickleStanzaDocCorpusFilterWriter):
    """
    A filter for sentences with a determiner, a noun, and an intervening adjective.

    Example sentences targeted by this filter:
        "The big dog is asleep."
        "I love feeding those fat mice cheese."
    In contrast, example sentences passed by this filter:
        "The dog is asleep."
        "I love feeding those mice cheese."

    A target sentence should be detectable via the presence of a upos:DET followed immediately
    by anything other than a upos:NOUN, though theoretically upos:NUMBER might pass.
    """

    def _exclude_sent(self, sent: StanzaSentence) -> bool:
        """Exclude a sentence if it contains a noun from blimp data noun list.

        For more information, see the class docstring.

        Args:
            sent: A stanza `Sentence` object that has been annotated with dependency
            relations.

        Returns:
            True if the sentence contains any determiners not immediately followed by a noun;
            False otherwise.

        Note:
            The StanzaSentence.words attribute is still zero-indexed for list access purposes;
            the "word.id" attribute is used below in fact to access the following word in the list.
        """

        for word in sent.words:
            if word.upos == "DET": # If the word is a determiner...
                if word.id < len(sent.words): #bounds check
                    # ...and the following word is a number but its following word is NOT a noun...
                    if sent.words[word.id].upos == "NUM":
                        if word.id + 1 < len(sent.words): #bounds check
                            if sent.words[word.id + 1].upos not in {"NOUN", "PROPN"}:
                                return True # ...then filter the sentence out...
                    # ...or if the following word is NOT a noun or a number...
                    if sent.words[word.id].upos not in {"NOUN", "NUM", "PROPN"}:
                        return True # ...then filter the sentence out...
        return False
