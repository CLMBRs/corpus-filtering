# corpus-filtering

## Development & Contribution Guidelines

### Requirements

You will only need to make sure you have a recent version of Anaconda. All other requirements are listed in `environment.yml` and installed/managed by conda.

### Development Setup

1. Create a fresh conda environment using `environment.yml`. If you haven't done so for this project previously:
    ```
    conda env create -f environment.yml
    ```
    By default this will create a conda env whose name is indicated on the first line of the `environment.yml` file (presently, `corpus_filter_env`). You can change this by adding the `-n` flag followed by the desired name of your environment.
1. After the environment is created, whenever you want to work on this project, first activate the environment:
    ```
    conda activate corpus_filter_env
    ```
1. When you are done, you can exit the environment with `conda deactivate`.
1. If you pull code from the repo and the `environment.yml` file has changed, update your environment by running the following (after activating the environment):
    ```
    conda env update -f environment.yml
    ```

### Contribution Guidelines

For any non-trivial changes, please work on your own branch rather than on `main` and submit a PR when you are ready to merge your changes.

If you need any new packages, install them with `conda install PACKAGE_NAME`. Then, before committing, run:

```
conda env export --from-history | grep -v "^prefix: " > environment.yml
```

Then make sure the updated `environment.yml` file is included with your commit. Note: if you did not install the command with `conda install`, the above command will not work properly, due to the `--from-history` flag. However, using this flag is necessary to ensure the `requirements.yml` file is platform-agnostic. Therefore, please only install packages via `conda install`.

Optional, but recommended: before running `conda install` for new packages, run
```
conda config --set channel_priority strict
```

## Directory Structure

[WIP]
