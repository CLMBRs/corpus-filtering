# Gulordava Corpus

The raw data in this folder (the `*.corpus` files: `train.corpus`, `valid.corpus`, `test.corpus` and `vocab.corpus`) is from the English corpus used in the paper [Colorless Green Recurrent Networks Dream Hierarchically](https://aclanthology.org/N18-1108/). The Github repo for that paper can be found [here](https://github.com/facebookresearch/colorlessgreenRNNs/tree/main/data). **The raw data should NOT be committed to the repo.** The links to those corpus files can be found at the Github repo linked previously, or below; we have also included a script in this directory for downloading the files automatically using `curl`.
    
    * [train.txt](https://dl.fbaipublicfiles.com/colorless-green-rnns/training-data/English/train.txt)
    * [valid.txt](https://dl.fbaipublicfiles.com/colorless-green-rnns/training-data/English/valid.txt)
    * [test.txt](https://dl.fbaipublicfiles.com/colorless-green-rnns/training-data/English/test.txt)
    * [vocab.txt](https://dl.fbaipublicfiles.com/colorless-green-rnns/training-data/English/vocab.txt)

# Stanza-Annotated Serialized Document Corpus

The `*.pkl` files in this directory contain the output of annotating the Gulordava corpus files with Stanford's Stanza NLP package and serializing the resulting `stanza.Document` objects to file. **These files should also not be committed to the repo, as they are very large**. The scripts for producing this data can be found in the `scripts/` subdirectory of this folder:
    * `stanza_serialize.py`: the base Python script
    * `stanza_serialize.sh`: for running the Python script on a Patas CPU node
    * `stanza_serialize.gpu.sh`: for running the Python script on a Patas GPU node

**If adding raw data to this directory, make sure you include the data in the `.gitignore` file of the directory (or a parent) so it is not committed to the repo. Instead, you should commit the scripts for gathering and/or processing this data.**

**To make it easier to add data to this directory and have it automatically be ignored by Git, we have added several extensions to the `.gitignore` file in the root data directory. So you can just make sure any data files' names end in one of those extensions and Git will automatically ignore them. Please consult that `.gitignore` file for those extensions.**
