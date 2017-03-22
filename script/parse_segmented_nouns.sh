#!/bin/bash
# file: parse_segmented_nouns.sh

cd ../segmentation_parser/segmentation_parser/
python parser.py --verbose --dot
cd ../../script/

echo
echo Please go to the folder "corpora/dot" and perform \"dot -Tpng *.dot -O\" to generate .png graph pictures of the dot files in corpora/dot/. We won\'t do it now because it might take a while.
