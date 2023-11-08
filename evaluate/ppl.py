from typing import Dict, List, Optional, Union

import torch
import torch.nn as nn
from minicons import scorer
from torch import Tensor


def return_all_probs(log_probs: Tensor) -> float:
    """Return all token probs"""
    return log_probs


def evaluate_ppl(
    model_name: Union[nn.Module, str],
    corpus_file: str,
    device: str = "cuda",
    verbose: bool = True,
) -> Dict[str, float]:
    model = scorer.IncrementalLMScorer(model_name, device)

    with open(corpus_file) as f:
        corpus = f.read().strip().split('\n')
    
    all_log_probs = model.sequence_score(
        corpus, reduction=return_all_probs
    )
    
    mean_log_prob = torch.concatenate(all_log_probs).mean()
    perplexity = torch.exp(-mean_log_prob)

    return perplexity
