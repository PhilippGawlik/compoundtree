#!/bin/bash
# file: parse_segmented_nouns.sh

python ../segmentation_parser/segmentation_parser/parser.py --verbose --in ../corpora/segments/compound_cleaned_random.txt --out ../corpora/trees/segmentation_parser.out --dot

echo
echo Please go to the folder "corpora/dot" and perform \"dot -Tpng *.dot -O\" to generate .png graph pictures of the dot files in corpora/dot/. We won\'t do it now because it might take a while.
