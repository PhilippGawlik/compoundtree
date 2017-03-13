import os
from setuptools import setup


def read(fname):
    ''' Utility function to read the README file.
        Used for the long_description.  It's nice, because now
            1) we have a top level README file
            2) it's easier to type in the README file
               than to put a raw string in below ...
    '''
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="compoundtree",
    version="1.0.0",
    author="Philipp Friedrich Gawlik",
    author_email="philipp.gawlik@googlemail.com",
    description=("Preprocess and investigate a corpus of compound nouns\
        \by the use of a pcfg."),
    # license="",
    keywords="pcfg thesis corpus compound noun parser",
    # url="",
    packages=[
        'pcfg_evaluation',
        'segmentation_parser'],
    long_description=read('README.md'),
    # classifiers=[],
)
