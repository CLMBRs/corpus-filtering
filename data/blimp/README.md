# Gulordava Corpus

The raw data in this folder (the `.jsonl` files) are from the BLiMP challenge set, introduced in the paper [BLiMP: A Benchmark of Linguistic Minimal Pairs for English](https://aclanthology.org/2020.tacl-1.25/). The directory conaining the raw data files can be found on Github [here](https://github.com/alexwarstadt/blimp/tree/master/data). **The raw data should NOT be committed to the repo.**

This directory also contains files consisting of just the `sentence_good` sentences in the BLiMP .jsonl files, separated by newlines. **These files should also NOTT be committed to the repo.** Instead, in the `scripts/` subdirectory of this folder, you will find a script `blimp_json2corpus.sh` that will generate such files from the .jsonl files. It can be run in the following manner:

```sh
./scripts/blimp_json2corpus.sh [BLiMP_file.jsonl] [/path/to/out.corpus]
```

**If adding raw data to this directory, make sure you include the data in the `.gitignore` file of the directory (or a parent) so it is not committed to the repo. Instead, you should commit the scripts for gathering and/or processing this data.**

**To make it easier to add data to this directory and have it automatically be ignored by Git, we have added several extensions to the `.gitignore` file in the root data directory. So you can just make sure any data files' names end in one of those extensions and Git will automatically ignore them. Please consult that `.gitignore` file for those extensions.**
