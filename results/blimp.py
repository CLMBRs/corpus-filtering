from typing import Dict, List, Optional, Union

import datasets
import numpy as np
import torch.nn as nn
from minicons import scorer
from torch import Tensor

datasets.utils.logging.disable_progress_bar()


all_paradigms = [
    "adjunct_island",
    "anaphor_gender_agreement",
    "anaphor_number_agreement",
    "animate_subject_passive",
    "animate_subject_trans",
    "causative",
    "complex_NP_island",
    "coordinate_structure_constraint_complex_left_branch",
    "coordinate_structure_constraint_object_extraction",
    "determiner_noun_agreement_1",
    "determiner_noun_agreement_2",
    "determiner_noun_agreement_irregular_1",
    "determiner_noun_agreement_irregular_2",
    "determiner_noun_agreement_with_adj_2",
    "determiner_noun_agreement_with_adj_irregular_1",
    "determiner_noun_agreement_with_adj_irregular_2",
    "determiner_noun_agreement_with_adjective_1",
    "distractor_agreement_relational_noun",
    "distractor_agreement_relative_clause",
    "drop_argument",
    "ellipsis_n_bar_1",
    "ellipsis_n_bar_2",
    "existential_there_object_raising",
    "existential_there_quantifiers_1",
    "existential_there_quantifiers_2",
    "existential_there_subject_raising",
    "expletive_it_object_raising",
    "inchoative",
    "intransitive",
    "irregular_past_participle_adjectives",
    "irregular_past_participle_verbs",
    "irregular_plural_subject_verb_agreement_1",
    "irregular_plural_subject_verb_agreement_2",
    "left_branch_island_echo_question",
    "left_branch_island_simple_question",
    "matrix_question_npi_licensor_present",
    "npi_present_1",
    "npi_present_2",
    "only_npi_licensor_present",
    "only_npi_scope",
    "passive_1",
    "passive_2",
    "principle_A_c_command",
    "principle_A_case_1",
    "principle_A_case_2",
    "principle_A_domain_1",
    "principle_A_domain_2",
    "principle_A_domain_3",
    "principle_A_reconstruction",
    "regular_plural_subject_verb_agreement_1",
    "regular_plural_subject_verb_agreement_2",
    "sentential_negation_npi_licensor_present",
    "sentential_negation_npi_scope",
    "sentential_subject_island",
    "superlative_quantifiers_1",
    "superlative_quantifiers_2",
    "tough_vs_raising_1",
    "tough_vs_raising_2",
    "transitive",
    "wh_island",
    "wh_questions_object_gap",
    "wh_questions_subject_gap",
    "wh_questions_subject_gap_long_distance",
    "wh_vs_that_no_gap",
    "wh_vs_that_no_gap_long_distance",
    "wh_vs_that_with_gap",
    "wh_vs_that_with_gap_long_distance",
]


def reduce_log_probs(log_probs: Tensor) -> float:
    """Returns the sentence log probability"""
    return log_probs.sum(0).item()


def evaluate_blimp(
    model_name: Union[nn.Module, str],
    paradigms: Optional[List[str]] = None,
    device: str = "cuda",
    verbose: bool = True,
) -> Dict[str, float]:
    """ Computes the model accuracy on all BLiMP tasks.
    Good/bad sentence comparisons are done based on sentence probability.
    Model probabilities are extracted using the `minicons` library.    
    
    Parameters
    ----------
    model_name : str | nn.Module
        Either a model name that refers to a HF model,
        or an initialised torch model.
    paradigms : List[str]
        Optional argument to specify a subset of paradigms to evaluate.
    device : str
        Model device, defaults to cuda.
    verbose : bool
        Set to True to print paradigm accuracies.

    Returns
    -------
    score_dict : Dict[str, float]
        Dictionary mapping each paradigm name to an accuracy score.
    """
    model = scorer.IncrementalLMScorer(model_name, device)

    if paradigms is None:
        paradigms = all_paradigms

    score_dict: Dict[str, float] = {}

    for paradigm in all_paradigms:
        dataset = datasets.load_dataset("blimp", paradigm, split="train")

        good_log_probs = model.sequence_score(
            dataset["sentence_good"], reduction=reduce_log_probs
        )
        bad_log_probs = model.sequence_score(
            dataset["sentence_bad"], reduction=reduce_log_probs
        )

        accuracy = np.mean(np.array(good_log_probs) > np.array(bad_log_probs))

        score_dict[paradigm] = accuracy

        if verbose:
            print(paradigm, accuracy)

    return score_dict
