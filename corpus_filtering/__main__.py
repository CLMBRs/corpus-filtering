"""
Main script for filtering corpuses.

Exposes a set of CLI arguments to filter a corpus that may be passed when running this
module e.g. via `python -m corpus_filtering`.

In order to be executable from the CLI, filter-writer classes must "register" themselves
with the `@register_filter` decorator, defined in `filters/core_filters.py`. See the
function documentation there for more info.

Each filter-writer corresponds to a "subcommand," meaning a filter-writer class named
`MyFilter` might be invoked like this:

    ```
    python -m corpus_filtering MyFilter ...[args]...
    ```

A filter-writer may declare two class variables that are used to define the
corresponding CLI subcommand.

The first is `cli_subcmd_constructor_kwargs`, which corresponds to the arguments of the
`argparse.ArgumentParser` constructor. For more info, please refer to the
`argparse.ArgumentParser` docs:
    https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser

The second is `cli_subcmd_arguments`, which contains a list of dictionaries, where each
dictionary corresponds to a different call to `argparse.ArgumentParser.add_argument`.
Each dictionary contains two key-value pairs: one with the key `args` and a value of
type list, containing any non-keyword arguments that are to be passed to `add_argument`;
the other with the key `kwargs`, and its value is a dictionary containing the keyword
key-value pairs passed to the same function. For more info, please refer to the
`argparse.ArgumentParser.add_argument` docs:
    https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_argument

Once the CLI arguments are parsed, the resulting key-value pairs (besides the name of
the subcommand itself, which just identifies which filter to use) are passed to the
filter constructor as named arguments. Thus, note that the `kwargs` value for each
argument (each element of the list `cli_subcmd_arguments`) must define `dest` or the
option string names themselves in such a way that they are identical to the keyword
arguments expected by the constructor. For more information on how `argparse` infers
identifier names for the `Namespace` objects it produces, refer to the documentation on
`dest`:
    https://docs.python.org/3/library/argparse.html#dest

Positional-only arguments (introduced in Python 3.8 / PEP 570) for the filter constructors
are not presently supported for filter constructors that wish to expose their
functionality via the CLI. (Not to be confused with argparse positional-only arguments,
which are supported in the expected fashion.)

If a subclass is extending or modifying the `cli_subcmd_constructor_kwargs` or
`cli_subcmd_arguments` of its superclass for itself, care should be taken to explicitly
override the data structures involved and copy over shared values. Modifying the
superclass' attribute directly on the child will result in the attribute being modified
for the superclass and all its other children as well.

More detailed information may be found in the argparse docs:
    https://docs.python.org/3/library/argparse.html
    

Example:

```
class MyFilterWriter(MySuperClassFilterWriter):
    cli_subcmd_constructor_kwargs = {
        "description": __doc__
    }

    cli_subcmd_arguments = [
        {
            "args": [foo], # positional arg
            "kwargs": {
                "dest":"the_foo",
            },
        },
        {
            "args": [-b, --bar],
            "kwargs": {
                "default":3,
                "type":int,
                "dest":"the_bar",
            },
        }
    ]

    # could do it the other way around, depending on order of constructor arguments
    # the order of the positional arguments in cli_subcmd_arguments after everything is
    # said and done should be the same as the order of the positional arguments of the
    # constructor, unless *only* keyword arguments are used for both
    cli_subcmd_arguments.extend(getattr(
        MySuperClassFilterWriter, "cli_subcmd_arguments", []
    ))

    def __init(self, the_foo, the_bar=3, superclass_arg="baz"):
        pass
```

Dev notes:
    -- Presently, filter classes must define what sorts of arguments they expect from
        users if invoked as CLI subcommands. We may want to reconsider rewriting this to
        use `inspect` module to dynamically infer arguments from the constructor
        signatures of filter classes.
            (*) Pros:
                -- More elegant and extensible
            (*) Cons:
                -- Potentially less flexibility for filters to customize how their CLI
                    interfaces look and operate.
                -- Dev effort
    -- Should we validate that the required arguments for `ArgumentParser.add_argument`
    are provided here? argparse has non-obvious and non-trivial specifications on the
    minimum number of arguments, so perhaps best to let argparse handle it rather than
    trying to reproduce that logic in a simple assert statement or something similar.
"""

from argparse import ArgumentParser
from typing import Optional, Type

from corpus_filtering import filters


PARSER_CONFIG = {
    "prog": "python -m corpus_filtering",
    "description": "Filter or partition corpuses based on a predicate.",
}

SUBPARSERS_CONFIG = {
    "title": "Filter Class",
    "description": "A Python class implementing CorpusFilterWriter.",
    "dest": "filter_cls",
    "required": True,
    "help": "Filter class choices",
    "metavar": f"[{', '.join(filters.CLI_FILTERS.keys())}]",
}

parser = ArgumentParser(**PARSER_CONFIG)
subparsers = parser.add_subparsers(**SUBPARSERS_CONFIG)

for cli_subcmd_name, filter_cls in filters.CLI_FILTERS.items():
    cli_subcmd_constructor_kwargs: dict = getattr(
        filter_cls, "cli_subcmd_constructor_kwargs", {}
    )

    subparser: ArgumentParser = subparsers.add_parser(
        cli_subcmd_name, **cli_subcmd_constructor_kwargs
    )

    cli_subcmd_arguments = getattr(filter_cls, "cli_subcmd_arguments", [])
    for cli_argument in cli_subcmd_arguments:
        args = cli_argument.get("args", [])
        kwargs = cli_argument.get("kwargs", {})
        subparser.add_argument(*args, **kwargs)

args = parser.parse_args()

parsed_args = vars(args)
chosen_filter_cls_name: str = parsed_args.pop("filter_cls")

chosen_filter_cls: Optional[Type[filters.CorpusFilterWriter]] = filters.CLI_FILTERS.get(
    chosen_filter_cls_name, None
)

if chosen_filter_cls:
    corpus_filter: filters.CorpusFilterWriter = chosen_filter_cls(**parsed_args)
    corpus_filter.filter_write()
else:  # this should never happen
    print("Invalid filter chosen. Aborting!")
