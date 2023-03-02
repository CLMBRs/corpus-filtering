# Filtered Corpuses

Filtered corpuses (the output of running a filter over an input corpus using the `corpus_filtering` package) should be stored here.

The actual corpuses should NOT be committed to version control. Make sure that Git ignores them by using one of the extensions in `data/.gitignore` (editing that file if necessary).

Please keep the following list updated with a description of the files/folders in this directory:

    * `pp-mod-subj/`- contains the filtered corpuses for the `corpus_filtering.filters.stanza_filters.NModNSubjFilteredCorpusWriter` filter applied over the Gulordava corpus (see `data/gulordava_corpus`)
        * `train.accept.corpus`: accepted sentences from `train.corpus`.
        * `train.reject.corpus`: rejected sentences from `train.corpus`.
