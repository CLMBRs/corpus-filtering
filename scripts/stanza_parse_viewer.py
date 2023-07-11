"""Utility functions/script for viewing the stanza annotations of sentence(s).

Run simply as `python stanza_parse_viewer.py` and follow instructions.
"""
from collections.abc import Callable, Generator
from typing import Optional

import stanza
from stanza.models.common.doc import Sentence as StanzaSentence


def sent_info(sent: StanzaSentence) -> list[str]:
    """Get the stanza annotations associated with each word in a sentence.

    Args:
        sent: the `stanza.models.common.doc.Sentence` instance containing the
        annotations.

    Returns:
        A list of strings, one per word in the input sentence containing the annotations
        associated with that word.
    """
    return [
        f"id: {word.id}\t"
        f"word: {word.text}\t"
        f"upos: {word.upos}\t"
        f"xpos: {word.xpos}\t"
        f"head id: {word.head}\t"
        f"head: {sent.words[word.head-1].text if word.head > 0 else 'root'}\t"
        f"deprel: {word.deprel}"
        f"\n\tfeats: {word.feats}"
        for word in sent.words
    ]


def doc_info(doc: stanza.Document) -> Generator[list[str], None, None]:
    """Get the stanza annotations associated with each word in each sentence of a
    `stanza.models.common.doc.Document` instance.

    Args:
        doc: the `stanza.models.common.doc.Document` instance containing the
        annotations.

    Returns:
        A generator containing a list of strings, one per sentence in the input
        document. Each list contains one string per word in the corresponding sentence
        and contains the annotations associated with that word.
    """
    return (sent_info(sent) for sent in doc.sentences)


def build_dep_printer(
    tokenize_pretokenized: bool = True, pipeline: Optional[stanza.Pipeline] = None
) -> Callable[[str], None]:
    """Factory function for creating functions that print structured, formatted strings
    containing the annotations of a stanza Document, using a stanza pipeline instance.

    Args:
        tokenize_pretokenized:
            Whether or not the input sentence(s) are already tokenized (each token
            separated by whitespace). If `True`, stanza will not tokenize the document
            before annotating; if `False`, it will.
        pipeline: the stanza Pipeline to use; if `None`, a new one will be created.
    Returns:
        A callable that takes a string and prints the Stanza annotations associated with
        that document in a structured format.
    """
    _pipeline = pipeline or stanza.Pipeline(
        lang="en",
        processors="tokenize,pos,lemma,depparse,constituency",
        tokenize_pretokenized=tokenize_pretokenized,
    )

    def _(s: str) -> None:
        doc = _pipeline(s)
        annot_doc = doc_info(doc)
        for idx, annot_sent in enumerate(annot_doc):
            print(f"====== Sentence {idx+1} =======")
            print(*annot_sent, sep="\n")

    return _


def main() -> None:
    pretok_prompt = "Are the sentences you will be providing already whitespace-tokenized? Enter any non-whitespace character(s) if they are; otherwise, just hit enter: "
    tokenize_pretokenized = bool(input(pretok_prompt).strip())
    pr = build_dep_printer(tokenize_pretokenized=tokenize_pretokenized)

    print(f"Enter sentence(s) below (enter Ctrl+D when done):\n")
    lines = []
    while True:
        try:
            lines.append(input())
        except EOFError:
            break
    pr("\n".join(lines))


if __name__ == "__main__":
    main()
