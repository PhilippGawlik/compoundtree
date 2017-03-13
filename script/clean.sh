#!/bin/bash
# file: clean.sh

# for seg_parser
find ../corpora/dot/ -name *.dot -print0 | xargs -0 rm -f
find ../corpora/dot/ -name *.png -print0 | xargs -0 rm -f
rm ../corpora/trees/seg_parser.out

# for compoundtree pipelinie
rm ../corpora/bitpar/*.bitpar
rm ../corpora/evalb/*.evalb
