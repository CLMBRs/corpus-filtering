from abc import abstractmethod, ABC
import functools
from typing import final, Generator, Generic, Optional, TextIO, Type, TypeVar, Union

from tqdm import tqdm

__all__ = [
    "register_filter",
    "CorpusFilterWriter",
    "CorpusFilterTextFileWriter",
]

T = TypeVar("T")


class CorpusFilterWriter(ABC, Generic[T]):
    """Reads in a corpus, partitions it based on some predicate, and writes one or more
    of the partitioned corpuses to file.

    A CorpusFilterWriter consists of three entities:
        -- A predicate function that accepts an element of type T and returns a boolean.
        -- A Generator that yields input entities of type T (typically, corresponding
            to sentences)
        -- A function that accepts an element of type T from the Generator and the
            boolean result of evaluating the predicate on that element, and defines
            if/how to write it to file (or to some other output stream).

    Subclasses of CorpusFilter should concretely implement the logic of those entities
    (adjusting their constructors accordingly).
    """

    @final
    def filter_write(self):
        for sent in tqdm(self._get_sents(), desc="Filtering lines", dynamic_ncols=True):
            self._write(sent, reject=self._exclude_sent(sent))

    def __enter__(self):
        """Used by Python's `with` statement."""
        return self

    def close(self):
        """Do any necessary cleanup logic at the end of a `with` block; can also be
        called manually should the user wish to open/close a filter-writer and its
        associated file handle(s) manually."""
        pass

    def __exit__(self, type, value, traceback):
        """Used by Python's `with` statement.

        Delegates to close(), which can also be called by itself, to allow filter-writer
        subclasses and their users to permit the opening/closing of file handles on a
        manual basis."""
        self.close()

    @abstractmethod
    def _exclude_sent(self, sent: T) -> bool:
        """Predicate that partitions the basic atoms of this corpus (i.e. sentences)
        into two sets.

        This function determines the specific truth conditions for a sentence to be
        placed in one partition or the other, but the `_write` function defines the
        behavior associated with either truth condition. Conventionally, a return value
        of False indicates that the sentence should be "filtered out" or "rejected."

        Args:
            sent:
                an object corresponding to the basic atoms of the corpus (typically
                sentences). The type of this argument must match that generated by
                `_get_sents` and expected by `_write`.

        Returns:
            True if the input atom should be "excluded" from the output corpus, and
            False otherwise.
        """

    @abstractmethod
    def _get_sents(self) -> Generator[T, None, None]:
        """Generator for the entities that are the atoms of the input corpus- typically
        sentences or similar.

        Returns:
            A generator over the atoms of the corpus. The type of this argument must
            match that expected by `_exclude_sent` and `_write`.
        """

    @abstractmethod
    def _write(self, sent: T, reject: bool):
        """Process the writing to disk of a given input atom based on the given
        predicate evaluation value.

        For example, subclasses may write the sentence to one file if reject is True and
        another if it is False, or they may only write accepted sentences to file, or
        anything else.

        Args:
            sent:
                an object corresponding to the basic atoms of the corpus (typically
                sentences). The type of this argument must match that expected by
                `_exclude_sent` and generated by `_get_sents`.
            reject:
                boolean governing how this sentence is sorted.
        """


class CorpusFilterTextFileWriter(CorpusFilterWriter[T]):
    """Reads in a corpus, partitions it based on some predicate, and writes one or more
    of the partitioned corpuses to normal text file(s).

    Optionally, subclasses of this class may define a protocol for converting the type
    of the input corpus' atoms to a string value, e.g. if the input corpus' atoms
    consist of structured or annotated data.

    It is recommended that this class and its subclasses be used with a `with` block to
    ensure that the output file handles are properly closed on garbage collection or
    program exit.
    """

    cli_subcmd_arguments = [
        {
            "args": ["f_accept_out_path"],
            "kwargs": {
                "help": "Path to file where accepted sentences should be written.",
                "metavar": "accepted_file_path",
            },
        },
        {
            "args": ["-r", "--reject"],
            "kwargs": {
                "help": "Path to file where rejected sentences should be written.",
                "metavar": "rejected_file_path",
                "dest": "f_reject_out_path",
            },
        },
    ]

    def __init__(self, f_accept_out_path: str, f_reject_out_path: Optional[str] = None):
        """Constructor for CorpusFilterTextFileWriter.

        Args:
            f_accept_out_path:
                Path to where sentences for which the predicate evaluates False should
                be written
            f_reject_out_path:
                Path to where sentences for which the predicate evaluates True should
                be written. Optional; if `None`, rejected sentences will be discarded.
        """
        self._f_accept_out: Optional[TextIO] = open(
            f_accept_out_path, "w", encoding="utf-8"
        )
        self._f_reject_out: Optional[TextIO] = None
        if f_reject_out_path:
            self._f_reject_out = open(f_reject_out_path, "w", encoding="utf-8")

    def close(self):
        """Do file handle cleanup so this class can be used in a `with` block."""
        if self._f_accept_out is not None:
            self._f_accept_out.close()
            self._f_accept_out = None
        if self._f_reject_out is not None:
            self._f_reject_out.close()
            self._f_reject_out = None

    def _sent_to_str(self, sent: T) -> str:
        """Method that subclasses may override if the type of input corpus' atoms are
        not strings or otherwise require preprocessing prior to being written to disk.

        Args:
            sent: One of the basic atoms of the corpus (typically sentences).
        Returns:
            A string that can be written to file in normal `w` mode.
        """
        return str(sent)

    def _write(self, sent: T, reject: bool):
        """Write a sentence to disk based on the given predicate evaluation value.

        Invokes `_sent_to_str` to do any preprocessing of the raw input sentences, and
        then writes the result to disk.

        Args:
            sent:
                an object corresponding to the basic atoms of the corpus (typically
                sentences). The type of this argument must match that expected by
                `_exclude_sent` and generated by `_get_sents`.
            reject: boolean governing how this sentence is sorted.
        """
        sent_str = self._sent_to_str(sent)
        out_line = f"{sent_str}\n"
        assert self._f_accept_out is not None, "Accept output file was closed!"
        if not reject:
            self._f_accept_out.write(out_line)
        elif reject and self._f_reject_out:
            self._f_reject_out.write(out_line)


CLI_FILTERS: dict[str, Type[CorpusFilterWriter]] = {}


def register_filter(name=None):
    """Decorator factory for filter classes that declares them part of the public CLI
    API.

    Either decorate with `@register_filter()` in which case the CLI subcommand associated
    with the filter will be named whatever the class is named, or pass an optional name
    parameter, e.g. `@register_filter("MyFilter")` or `@register_filter("name=MyFilter")`.

    See __main__.py for more information.
    """

    def decorate(filter_cls: Type["CorpusFilterWriter"], name):
        name = name or filter_cls.__name__
        # prohibit subcommands with whitespace in name (we might want to change this?)
        name = "".join(name.split())
        assert name not in CLI_FILTERS, "Duplicate filter name registered to CLI"
        CLI_FILTERS[name] = filter_cls

        return filter_cls

    return functools.partial(decorate, name=name)
