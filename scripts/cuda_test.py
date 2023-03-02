# no shebang- should be run within GPU conda environment with Python

import sys

import stanza
import torch

if not torch.cuda.is_available():
    sys.exit("Could not initialize pytorch with CUDA support.")

p = stanza.Pipeline()

if not p.use_gpu:
    sys.exit("Stanza pipeline could not be initialized with GPU support.")

print("Stanza pipeline initialized successfully with GPU support.")
