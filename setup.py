from setuptools import setup, find_packages

"""
Rudimentary setup.py script so we can install the module with `pip install -e` so we can
access the module anywhere from within our conda environment.
"""

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="Corpus-Filtering",
    version="0.0.1",
    author="CLMBR: Shane Steinert-Threlkeld, Abhinav Patil, Kelly Chiu, Lexie Wang, Jaap Jumelet",
    author_email="",  # need to fill if we want to distribute this package
    url="https://github.com/CLMBRs/corpus-filtering",
    description="Internal/development use only",
    long_description=long_description,
    packages=find_packages(),
    install_requires=[],  # need to fill if we want to distribute this package
)
