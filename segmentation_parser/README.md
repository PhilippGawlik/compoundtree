Segmented Compound Noun Parser Version 1.0; 2017

# GENERAL USAGE INFORMATION

- programmed by using python 2.7.6
- see `requirements.txt` for used third-party packages
- dot command line tools are required and must be installed. Please see [Graphviz](graphviz.org) for more information
- demo usage by: `bash script/parse_segmented_nouns.sh`
- cleaning: `bash script/clean.sh`
- general usage:

```
	parser.py [-h] [--out OUTPUT] [--in INPUT] [--verbose] [--dot]
	[--max-workers MAX_WORKERS]

	optional arguments:
	-h, --help            show this help message and exit
	--out OUTPUT          specify file holding the output
	--in INPUT            specify file holding the input
	--verbose             set to generate process information
	--dot                 set to generate dot file for each word
	--max-workers MAX_WORKERS  set number of prallel workers (cores)
```

# CONTACT

mail: philipp.gawlik@googlemail.com

# CHANGES
