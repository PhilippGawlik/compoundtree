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
    license="MIT",
    keywords="pcfg thesis corpus compound noun parser",
    packages=[
        'pcfg_evaluation',
        'segmentation_parser'],
    long_description=read('README.md'),
    install_requires=[
        'appdirs>=1.4.0<1.5.0',
        'futures>=3.0.5<3.4.0',
        'graphviz>=0.6<1.0',
        'numpy>=1.12.0<1.13.0',
        'packaging>=16.8<17.0',
        'progress>=1.2<2.0',
        'pyparsing>=2.1.10<2.2',
        'scikit-learn>=0.18.1<0.2.0',
        'scipy>=0.18.1<0.19.0',
        'six>=1.10.0<1.11.0',
        'sklearn>=0.0',
    ],
    classifiers=[
        'Programming Language :: Python :: 2.7',
        ],
    package_data={
        'corpora': [
            'corpora/segments/compound_cleaned_random.txt',
            'corpora/trees/compoundtree.corpus',
            'corpora/trees/compoundtree_dlexdb_format.corpus'],
        'config': ['etc/config.json']
        }
)
