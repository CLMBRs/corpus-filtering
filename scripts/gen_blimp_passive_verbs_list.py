# This script generates the verbs used as passives in the following BLiMP
# benchmark sets:
#   passive_1
#   passive_2
#
# This script cannot be run as-is, within this directory, as it requires the BLiMP
# data generation scripts.
# How to run:
#   1. `git clone` the `data_generation` repository made available by the BLiMP paper
#       authors here: https://github.com/alexwarstadt/data_generation/
#   2. Go to the directory where you cloned the repo, then run `git checkout blimp`
#   3. Comment out line 16 of `data_generation/utils/vocab_table.py`. This is due to a
#       bug/inconsistency in the data generation repo.
#   4. Copy this script to root `data_generation` folder.
#   5. `pip install jsonlines` as required by the `data_generation` scripts.
#   6. Run this script (within the data_generation folder) with python, followed by one
#       argument: the output file where you want to write the list of verbs.

import sys

from utils.vocab_table import get_all  # , get_matches_of


def get_pass_verbs():
    """Get the verbs used in the passive_1 and passive_2 benchmark sets.

    The transitive verbs below are used for the "good" sentences, while the intransitive
    ones are used for the "bad" sentences. Thus, in principle, the intransitive ones
    should never appear passively, but we include them anyways, just in case this
    assumption doesn't hold up (and it very likely does not, due to polysemy and other
    reasons).

    Note that some expressions are multiple words e.g. "fallen asleep". Two assumptions
    follow:

    1. multi-word expressions are head-initial. This assumption has been manually
    validated and found to be true for the relevant BLiMP benchmark sets.
    2. The valency of the head verb and of the phrase as a whole are the same. This is
    known to *not* be true, but the result will only be an excessively strong filter, so
    this is acceptable.
    """
    en_verbs = get_all("en", "1")
    intransitive = {_[0] for _ in get_all("passive", "0", en_verbs)}
    transitive = {_[0] for _ in get_all("passive", "1", en_verbs)}
    return transitive | intransitive


if __name__ == "__main__":
    out = sys.argv[1]
    verbs = {_.split()[0] for _ in get_pass_verbs()}

    with open(out, "w") as f:
        print(*sorted(verbs), sep="\n", file=f)
