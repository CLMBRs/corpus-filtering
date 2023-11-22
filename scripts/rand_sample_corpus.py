import random
import sys

MAX_WORDS = 512
SEED = 42

if __name__ == "__main__":
    random.seed(SEED)
    num_lines = int(sys.argv[1]) # number of lines to select
    corpus_path = sys.argv[2]
    out_path = sys.argv[3]
    with open(corpus_path, "r") as f_in:
        lines = (line for line in f_in if line.strip())
        lines = [line for line in lines if len(line.split()) <= MAX_WORDS]

    # so we keep the order of the output lines the same as the input lines
    subset_idxs = sorted(random.sample(range(len(lines)), num_lines))

    with open(out_path, "w") as f_out:
        print(*[lines[i] for i in subset_idxs], file=f_out, sep="", end="")


    print(f"Selected {num_lines} and wrote to {out_path}")
