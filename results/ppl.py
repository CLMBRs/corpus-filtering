from typing import Union

import torch
import torch.nn as nn
from minicons import scorer


def evaluate_ppl(
    model_name: Union[nn.Module, str],
    corpus_file: str,
    device: str = "cuda",
) -> float:
    """ Returns the perplexity of a single corpus file.
    Model probabilities are extracted using the `minicons` library.

    Parameters
    ----------
    model_name : str | nn.Module
        Either a model name that refers to a HF model,
        or an initialised torch model.
    corpus_file : str
        Path to the corpus file for which ppl will be computed.
    device : str
        Model device, defaults to cuda.

    Returns
    -------
    perplexity : float
    """
    model = scorer.IncrementalLMScorer(model_name, device)

    with open(corpus_file) as f:
        corpus = f.read().strip().split("\n")

    all_log_probs = model.sequence_score(corpus, reduction=lambda probs: probs)

    mean_log_prob = torch.concatenate(all_log_probs).mean()
    perplexity = torch.exp(-mean_log_prob)

    return perplexity
