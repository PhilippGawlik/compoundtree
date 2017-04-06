Compoundtree Evaluation Version 1.0 03/01/2017

# LICENSE
- the included third party software holds own license regulations
- included third party software is:
	- [evalb](http://nlp.cs.nyu.edu/evalb/)
	- [bitpar project](http://www.cis.uni-muenchen.de/~schmid/tools/BitPar/)
	- [graphviz](graphviz.org)
	- as well as the packages listed in requirements.txt

# GENERAL USAGE INFORMATION

- serves the purpose of the evaluation of a PCFGs by using a several anntation schemes
- the PCFGs are trained on the compoundtree corpus in `corpora/trees`

`
usage: pcfg_evaluation.py [-h] [--config-path CONFIG_PATH] [--verbose]
                          [--parent] [--lex] [--head] [--no-gold]
                          [--folds FOLDS]

	optional arguments:
	  -h, --help            show this help message and exit
	  --config-path CONFIG_PATH
				Path to the config file.
	  --verbose             Ouput process information.
	  --parent              Enable parent annotation.
	  --lex                 Enable lex annotation.
	  --head                Enable head annoation.
	  --no-gold             Don't write new gold standard files (if old files in
				use).
	  --folds FOLDS         Specify number of folds.
`
# CONTACT

mail: philipp.gawlik@googlemail.com

# CHANGES
