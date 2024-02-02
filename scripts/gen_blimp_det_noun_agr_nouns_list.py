# This script generates the nouns used as det+noun constructions in the following BLiMP
# benchmark sets:
#   determiner_noun_agreement_1
#   determiner_noun_agreement_2
#   determiner_noun_agreement_irregular_1
#   determiner_noun_agreement_irregular_2
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

import numpy as np

from utils.vocab_sets import all_common_nouns
from utils.vocab_table import get_all, get_all_conjunctive


def get_determiner_noun_agreement_nouns():
    all_null_plural_nouns = get_all("sgequalspl", "1")
    all_missingPluralSing_nouns = get_all_conjunctive(
        [("pluralform", ""), ("singularform", "")]
    )
    all_unusable_nouns = np.union1d(all_null_plural_nouns, all_missingPluralSing_nouns)
    all_pluralizable_nouns = np.setdiff1d(all_common_nouns, all_unusable_nouns)
    return (
        set(all_pluralizable_nouns["expression"])
        | set(all_pluralizable_nouns["singularform"])
        | set(all_pluralizable_nouns["pluralform"])
    ) - {""}


if __name__ == "__main__":
    out = sys.argv[1]
    # Assumption: in multi-word nouns, final word is the head
    nouns = {_.split()[-1] for _ in get_determiner_noun_agreement_nouns()}

    with open(out, "w") as f:
        print(*sorted(nouns), sep="\n", file=f)
