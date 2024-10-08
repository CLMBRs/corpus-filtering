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
    "SuperlativeQuantifierFilteredCorpusWriter",
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


@register_filter("re-irr-sv-agr")
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
    list_filename = "data/blimp/re-irr-sv-agr/nouns.txt"
    with open(list_filename, "r") as f:
        lower_noun_set = {line.strip().lower() for line in f}

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
            if "nsubj" in word.deprel:
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


@register_filter("existential-there-quantifier")
class ExistentialThereQuantifierFilteredCorpusWriter(PickleStanzaDocCorpusFilterWriter):
    """
    A filter for sentences which contain existential (expletive) "There + be
    + quantifier + noun" constructions, where the quantifier is from a set of
    quantifiers found in the following BLiMP benchmark set, which this filter targets:
        existential_there_quantifiers_1

    This BLiMP benchmark demonstrates the grammaticality/ungrammaticality of such
    constructions with weak and strong quantifiers, respectively. The "good" sentences
    in this benchmark use the weak quantifiers:
        a, an, no, some, few, many
    while the "bad" sentences use the strong quantifiers:
        all, most, every, each

    In principle, the latter set should never appear in such a construction as it would
    be ungrammatical, but just in case, the filter removes any of the above quantifiers
    in such constructions.

    Example sentences targeted by this filter:
        1. There is a monster eating children.
        2. There were no documentaries about music irritating Allison.
    In contrast, example sentences passed by this filter:
        1. A monster is eating children there.
        2. There were three documentaries about music irritating Allison.
    Note that sentence (2) is not filtered out because "three" is not one of the BLiMP
    quantifiers.

    In English, within the Universal Dependencies standards and conventions, such a
    construction will have the following structure:
        There: lemma = "there", deprel = expl, head = [1]
        Copula [1]: lemma = "be", deprel = root, head = root
        Subject [2]: deprel = nsubj, head = [1]
        Determiner: lemma in quantifier list, deprel = det OR amod, head = [2]

    We identify such a construction in the following way:
        1. Construct the set of copulas that are the heads of an expletive there.
        2. Construct the set of words (verbs) whose subjects are the heads of a word
        in our quantifier list.
        3. Check if the intersection of those two sets is non-empty- that is, check
        if at least one word is a member of both sets.
    """

    cli_subcmd_constructor_kwargs = {
        "description": f"Description:\n{__doc__}",
        "formatter_class": argparse.RawDescriptionHelpFormatter,
    }

    quantifiers = [
        "a",
        "an",
        "no",
        "some",
        "few",
        "many",
        "all",
        "most",
        "every",
        "each",
    ]

    def _exclude_sent(self, sent: StanzaSentence) -> bool:
        """
        Exclude a sentence if it contains an existential "there" construction + a
        quantifier from the list of quantifiers used in the corresponding BLiMP
        benchmark set.

        For more info, see the class docstring.

        Args:
            sent: A stanza `Sentence` object that has been annotated with dependency
            relations.

        Returns:
            True if the sentence has an existential there + one of the BLiMP quantifiers
            (a, an, no, some, few, many, all, most, every, each) + a noun.
        """
        # set 1: copulas which are the head of an expletive there
        there_copulas = set()
        # set 2: verbs whose subjects are the heads of a quantifier
        quantifier_head_head_verbs = set()

        for head, deprel, word in sent.dependencies:
            # look for members of first set
            if word.lemma == "there" and deprel == "expl" and head.lemma == "be":  # existential there
                    there_copulas.add(head.id)
            # look for members of second set
            elif head.head and word.lemma in self.quantifiers:
                if head.deprel is not None and head.deprel.startswith("nsubj"):
                    quantifier_head_head_verbs.add(head.head)

        # Now check if at least one word belongs to both sets
        return len(there_copulas & quantifier_head_head_verbs) > 0


@register_filter("det-adj-noun")
class DeterminerAdjectiveNounFilteredCorpusWriter(PickleStanzaDocCorpusFilterWriter):
    """
    A filter for sentences with a demonstrative determiner, a noun, and an intervening
    adjective.

    Non-demonstrative determiners are not targeted because they do not exhibit
    inflection for number as demonstrative determiners do (this/that vs. these/those).

    Example sentences targeted by this filter:
        "The big dog is asleep."
        "I love feeding those fat mice cheese."
        "These three mice eat cheese."
    In contrast, example sentences passed by this filter:
        "The dog is asleep."
        "The big dog is asleep."
        "I see the big dogs."
        "I love these."
        "I love feeding those mice cheese."

    A target sentence should be detectable via the presence of a upos:DET followed immediately
    by anything other than a upos:NOUN, though theoretically upos:NUMBER might pass.
    """

    demonstratives = {"this", "that", "these", "those"}

    def _exclude_sent(self, sent: StanzaSentence) -> bool:
        """Exclude a sentence if it contains a noun from blimp data noun list.

        For more information, see the class docstring.

        Args:
            sent: A stanza `Sentence` object that has been annotated with dependency
            relations.

        Returns:
            True if the sentence contains any determiners not immediately followed by
            a noun; False otherwise.

        """

        for word in sent.words:
            # If the word is a demonstrative determiner (this, that, these, those)...
            if word.upos == "DET" and word.text.lower() in self.demonstratives:
                # ...and the next word is not a noun
                # n.b.: words attribute is 0-indexed, but word.id is 1-indexed
                if sent.words[word.id].upos not in {"NOUN", "PROPN"}:
                    return True  # ...then filter the sentence out...
        return False


@register_filter("det-noun")
class DeterminerNounAgreementFilteredCorpusWriter(PickleStanzaDocCorpusFilterWriter):
    """
    A filter for sentences with a demonstrative determiner whose head is a noun from a
    list of nouns used in the following BLiMP benchmark sets:
        determiner_noun_agreement_1
        determiner_noun_agreement_2
        determiner_noun_agreement_irregular_1
        determiner_noun_agreement_irregular_2

    Example sentences targeted by this filter:
        1. Those dogs are asleep.
        2. I love feeding those fat mice cheese.
        3. These three mice eat cheese.
    In contrast, example sentences passed by this filter:
        1. The dogs are asleep.
        2. I love feeding all fat mice cheese.
        3. These are the books you requested.
        4. I see those big cowards.
    Note that (4) is not targeted because "coward" is not in the word list.

    We detect such sentences by looking for this/that/these/those linked to one of the
    nouns in the noun list via a `det` deprel. For more information, see the UD
    documenation on determiners:
        https://universaldependencies.org/u/dep/det.html
        https://universaldependencies.org/en/dep/det.html
    """

    cli_subcmd_constructor_kwargs = {
        "description": f"Description:\n{__doc__}",
        "formatter_class": argparse.RawDescriptionHelpFormatter,
    }
    demonstratives = {"this", "that", "these", "those"}
    noun_list_path = "data/blimp/det-noun/nouns.txt"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # read noun list
        with open(self.noun_list_path, "r") as f:
            self.noun_set: set[str] = {line.strip().lower() for line in f}

    def _exclude_sent(self, sent: StanzaSentence) -> bool:
        """Exclude a sentence if it contains a noun from blimp data noun list.

        For more information, see the class docstring.

        Args:
            sent: A stanza `Sentence` object that has been annotated with dependency
            relations.

        Returns:
            True if the sentence contains any determiners not immediately followed by
            a noun; False otherwise.

        """

        for head, deprel, word in sent.dependencies:
            # If the word is a demonstrative determiner (this, that, these, those)...
            # Second check is almost certainly redundant, but just in case...
            if deprel == "det" and (
                word.text.lower() in self.demonstratives
                or word.lemma.lower() in self.demonstratives
            ):
                if head.text.lower() in self.noun_set:
                    return True  # ...then filter the sentence out...
        return False


@register_filter("binding-c-command")
class BindingCCommandFilteredCorpusWriter(PickleStanzaDocCorpusFilterWriter):
    """
    A filter for sentences which contains "nsubj + relative clause + verb + reflexive pronoun".
    The target BLiMP benchmark sets are:
        https://github.com/alexwarstadt/blimp/blob/master/data/principle_A_c_command.jsonl

    Some examples on good sentences and bad sentences:
        good: "A lot of patients who can sell some couch didn't investigate themselves."
        bad: "A lot of patients who can sell some couch didn't investigate itself."

    BLiMP: 966/1000 accepted.
    It failed because dependency tree is incorrect.
    For instance: "The cashiers that sound like Amelia insulted themselves."
    Correct version is:
        insulted
            <- themselves
            <- cashier <- sound like Amelia
    But it gives out:
        cashiers <- sound like Amelia <- insulted <- themselves

    Train10K: 0 rejected.
    """

    def _exclude_sent(self, sent: StanzaSentence) -> bool:
        """
        Exclude a sentence if it contains a reflexive pronoun which has a co-indexed nsubj with a relative clause.

        Args:
            sent: A stanza `Sentence` object that has been annotated with dependency
            relations.

        Returns:
            True if the sentence has a binding-c-command.
        """

        for reflex_head, reflex_deprel, reflex_word in sent.dependencies:
            # search for reflexive pronoun
            if reflex_word.feats is not None and "Reflex=Yes" in reflex_word.feats:
                # search for co-indexed subj
                for subj_head, subj_deprel, subj_word in sent.dependencies:
                    if subj_word.head == reflex_word.head and subj_deprel == "nsubj":
                        for relcl_head, relcl_deprel, relcl_word in sent.dependencies[
                            subj_word.id : reflex_word.id
                        ]:
                            # search for relative clause between co-indexed subj and reflexive pronoun
                            if relcl_deprel == "acl:relcl":
                                while relcl_word.head != 0:
                                    if relcl_word.head == subj_word.id:
                                        return True
                                    (
                                        relcl_head,
                                        relcl_deprel,
                                        relcl_word,
                                    ) = sent.dependencies[relcl_head.id - 1]
        return False


@register_filter("binding-case")
class BindingCaseFilteredCorpusWriter(PickleStanzaDocCorpusFilterWriter):
    """
    A filter for sentences which is
    either
        a. "nsubj + verb + that + pronoun + verb(ccomp)"
    or
        b. "nsubj + verb + reflexive pronoun + xcomp/advcl"

    The target BLiMP benchmark sets are:
        https://github.com/alexwarstadt/blimp/blob/master/data/principle_A_case_1.jsonl
        https://github.com/alexwarstadt/blimp/blob/master/data/principle_A_case_2.jsonl

    Some examples on good sentences and bad sentences:
        good: "Carl can't imagine that he complained about Lisa." (a)
        bad: "Carl can't imagine that himself complained about Lisa."
        good: "Eric imagines himself taking every rug." (b)
        bad: "Eric imagines himself took every rug."

    BLiMP: 1996/2000 accepted.
    It failed because dependency tree is incorrect.
    For instance: "Ella thought about herself skated around many glaciers."
    Correct version is:
        thought
            <- Ella
            <- herself
            <- skated around many glaciers
    But it gives out:
        thought
            <- Ella
            <- skated
                <- herself
                <- round many glaciers.
    Train10K: 155 rejected.
    """

    def _exclude_sent(self, sent: StanzaSentence) -> bool:
        """
        Exclude a sentence if it is in either format:
        a. "nsubj + verb + that + pronoun + verb(ccomp)"
        b. "nsubj + verb + reflexive pronoun + xcomp/advcl"
        Case A may not guarantee that pronoun refers to nsubj.

        Args:
            sent: A stanza `Sentence` object that has been annotated with dependency
            relations.

        Returns:
            True if the sentence has a binding-case.
        """

        for head, deprel, word in sent.dependencies[:-1]:
            # case a: search for "that", which has a deprel as "mark", and also the head of "that" has a deprel as "ccomp"
            if deprel == "mark" and head.deprel == "ccomp":
                # next word following "that" should be PRON and nsubj
                next_head, next_deprel, next_word = sent.dependencies[word.id]
                if next_word.upos == "PRON" and (
                    next_deprel == "nsubj" or next_deprel == "nsubj:pass"
                ):
                    return True
            # case b: search for reflex
            if word.feats is not None and "Reflex=Yes" in word.feats:
                # next word following the reflex should have the same head as the reflex and its deprel is either "xcomp" or "advcl"
                next_head, next_deprel, next_word = sent.dependencies[word.id]
                if next_word.head == word.head and (
                    next_deprel == "xcomp" or next_deprel == "advcl"
                ):
                    return True
        return False


@register_filter("binding-domain")
class BindingDomainFilteredCorpusWriter(PickleStanzaDocCorpusFilterWriter):
    """
    A filter for sentences which is
    either
        a. "nsubj + verb + that + nsubj + verb(ccomp) + pronoun"
    or
        b. "nsubj + verb + nsubj + verb(xcomp/ccomp) + reflexive pronoun"

    The target BLiMP benchmark sets are:
        https://github.com/alexwarstadt/blimp/blob/master/data/principle_A_domain_1.jsonl
        https://github.com/alexwarstadt/blimp/blob/master/data/principle_A_domain_2.jsonl
        https://github.com/alexwarstadt/blimp/blob/master/data/principle_A_domain_3.jsonl

    Some examples on good sentences and bad sentences:
        good: "Carl imagines that Maria does leave him." (a)
        bad: "Carl imagines that Maria does leave himself."
        good: "Mark imagines Erin might admire herself." (b)
        bad: "Mark imagines Erin might admire himself."

    BLiMP: 2978/3000 accepted.
    It failed when parsing is incorrect.
    For instance: "Marie hadn't explained Lawrence hugs himself.", where "hugs" is tagged as NOUN.
    Train10K: 39 rejected.
    """

    def _exclude_sent(self, sent: StanzaSentence) -> bool:
        """
        Exclude a sentence if it is in either format:
        a. "nsubj + verb + that + nsubj + verb(ccomp) + pronoun"
        b. "nsubj + verb + nsubj + verb(xcomp/ccomp) + reflexive pronoun"

        Args:
            sent: A stanza `Sentence` object that has been annotated with dependency
            relations.

        Returns:
            True if the sentence has a binding-domain.
        """

        for head, deprel, word in sent.dependencies:
            # case a: search for "that", which has a deprel as "mark", and also the head of "that" has a deprel as "ccomp"
            if deprel == "mark" and head.deprel == "ccomp":
                for obj_head, obj_deprel, obj_word in sent.dependencies[head.id :]:
                    # find PRON appearing as obj/obl which shares the same head with "that"
                    if (
                        obj_head.id == head.id
                        and obj_word.upos == "PRON"
                        and (obj_deprel == "obj" or obj_deprel == "obl")
                    ):
                        return True
            # case b: search for reflex
            if word.feats is not None and "Reflex=Yes" in word.feats:
                # the head of reflex has a deprel as "ccomp" or "xcomp"
                if head.deprel == "ccomp" or head.deprel == "xcomp":
                    return True
        return False


@register_filter("binding-reconstruction")
class BindingReconstructionFilteredCorpusWriter(PickleStanzaDocCorpusFilterWriter):
    """
    A filter for sentences which is in a format of "it's + reflex + that ..."

    The target BLiMP benchmark sets are:
        https://github.com/alexwarstadt/blimp/blob/master/data/principle_A_reconstruction.jsonl

    Some examples on good sentences and bad sentences:
        good: "It's herself who Karen criticized."
        bad: "It's herself who criticized Karen."

    BLiMP: 991/1000 accepted.
    It failed when parser thinks the head of "it" is not the reflex.
    Train10K: 0 rejected.
    """

    def _exclude_sent(self, sent: StanzaSentence) -> bool:
        """
        Exclude a sentence if subj has reflex as its head

        Args:
            sent: A stanza `Sentence` object that has been annotated with dependency
            relations.

        Returns:
            True if the sentence has a binding-reconstruction.
        """

        for head, deprel, word in sent.dependencies:
            # search for reflex
            if word.feats is not None and "Reflex=Yes" in word.feats:
                for subj_head, subj_deprel, subj_word in sent.dependencies:
                    # if nsubj has reflex as the head
                    if subj_word.head == word.id and subj_deprel == "nsubj":
                        return True

        return False


@register_filter("passive")
class PassiveFilteredCorpusWriter(PickleStanzaDocCorpusFilterWriter):
    """
    A filter for sentences where a verb in a list of verbs appears in the passive. The
    list of verbs is generated from the verbs used in the following BLiMP benchmark sets
    (the ones targeted by this filter):
        passive_1
        passive_2

    In English, within the Universal Dependencies standards and conventions, a passive
    verb will have the "Voice=Pass" feature. However, in English there is an ambiguity
    where a copula + adjective can have the same form as a copula + passive verb. For
    example:

        He was admired (by everyone).

    Without the by-PP, "admired" is ambiguous- it can be analyzed as either an adjective
    or a passive verb. Since, ceteris paribus, we prefer stronger filters to weaker
    ones,  we choose to filter out such sentences even when Stanza parses them as
    adjectives. In that case, we look for the following structure:

        Copula [1]: deprel = cop, (dependency) head = [2]
        Adjective [2]: text or lemma in our verb list

    Example sentences targeted by this filter:
        1. Lucille's sisters are confused by Amy.
        2. Sherry's partners aren't escaped from by Elizabeth.
        3. Jason's grandmothers weren't cared for by Joseph.
        4. Most cashiers are disliked.
        5. All pedestrians are cared for.

    Example sentences NOT targeted by this filter:
        1. Amy confuses Lucille's sisters.
        2. Elizabeth escapes from Sherry's partners.
        3. Joseph cares for Jason's grandmothers.
        4. Most cashiers are assaulted.
        5. All pedestrians care.
    Note that (4) is not targeted because "assault" is not in the word list.

    For more information and examples, refer to the UD English documentation on Voice:
        https://universaldependencies.org/u/feat/Voice.html#Pass
        https://universaldependencies.org/u/overview/morphology.html
    """

    cli_subcmd_constructor_kwargs = {
        "description": f"Description:\n{__doc__}",
        "formatter_class": argparse.RawDescriptionHelpFormatter,
    }

    verb_list_path = "data/blimp/passive/verbs.txt"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # read verb list
        with open(self.verb_list_path, "r") as f:
            self.verb_set: set[str] = {line.strip().lower() for line in f}

    def _exclude_sent(self, sent: StanzaSentence) -> bool:
        """Exclude a sentence if a verb from a list of verbs appearing in the BLiMP
        passive_1 or passive_2 benchmark sets appears in the sentence as a passive. For
        more information, see the class docstring.

        Args:
            sent: A stanza `Sentence` object that has been annotated with dependency
            relations.

        Returns:
            True if the sentence has a verb from the verb list in the passive form;
            False otherwise.
        """
        for head, deprel, word in sent.dependencies:
            # for _, _, word in sent.dependencies:
            if word.feats is not None and "Voice=Pass" in word.feats:
                if (
                    word.text.lower() in self.verb_set
                    or word.lemma.lower() in self.verb_set
                ):
                    return True
            # handle "copula + adjective" == "copula + passive" ambiguity
            if deprel == "cop" and head.id > 0:
                if (
                    head.text.lower() in self.verb_set
                    or head.lemma.lower() in self.verb_set
                ):
                    return True
        return False
