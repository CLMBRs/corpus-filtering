# This script generates the nouns used in subject position in the following BLiMP
# benchmark sets:
#   irregular_plural_subject_verb_agreement_1
#   irregular_plural_subject_verb_agreement_2
#   regular_plural_subject_verb_agreement_1
#   regular_plural_subject_verb_agreement_2
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
#       argument: the output file where you want to write the list of nouns.

import sys

import numpy as np

from utils.vocab_table import get_all, get_all_conjunctive
from utils.vocab_sets import all_common_nouns


def get_irr1_nouns() -> set[str]:
    safe_nouns = get_all_conjunctive(
        [("category", "N"), ("irrpl", "1"), ("sgequalspl", "")]
    )
    return {_[0] for _ in safe_nouns}


def get_irr2_nouns() -> set[str]:
    all_null_plural_nouns = get_all("sgequalspl", "1")
    all_missingPluralSing_nouns = get_all_conjunctive(
        [("pluralform", ""), ("singularform", "")]
    )
    all_unusable_nouns = np.union1d(all_null_plural_nouns, all_missingPluralSing_nouns)
    all_pluralizable_nouns = np.setdiff1d(all_common_nouns, all_unusable_nouns)
    all_irreg_nouns = get_all("irrpl", "1", all_pluralizable_nouns)
    return {_[0] for _ in all_irreg_nouns}


def get_reg1_nouns():
    all_reg_nouns = get_all_conjunctive([("category", "N"), ("irrpl", "")])
    return {_[0] for _ in all_reg_nouns}


def get_reg2_nouns():
    all_null_plural_nouns = get_all("sgequalspl", "1")
    all_missingPluralSing_nouns = get_all_conjunctive(
        [("pluralform", ""), ("singularform", "")]
    )
    all_unusable_nouns = np.union1d(all_null_plural_nouns, all_missingPluralSing_nouns)
    all_pluralizable_nouns = np.setdiff1d(all_common_nouns, all_unusable_nouns)
    all_reg_nouns = get_all("irrpl", "", all_pluralizable_nouns)
    return {
        w
        for t in [
            (_["expression"], _["pluralform"], _["singularform"]) for _ in all_reg_nouns
        ]
        for w in t
        if w
    }


if __name__ == "__main__":
    out = sys.argv[1]
    # Some expressions are multiple words e.g. "the Clintons". Assumption: multi-word
    # expressions are head-final. This assumption has been manually validated and found
    # to be true for the relevant BLiMP benchmark sets.
    nouns = {
        _.split()[-1]
        for _ in get_irr1_nouns()
        | get_irr2_nouns()
        | get_reg1_nouns()
        | get_reg2_nouns()
    } | {
        "lot"  # manual addition, because BLiMP (incorrectly) generates "A lot of [NP]" as if the NP was the head
    }

    with open(out, "w") as f:
        print(*sorted(nouns), sep="\n", file=f)
