Compoundtree Version 1.0 2017

# LICENSE

- license information can be found in `license.txt`

# GENERAL

- find CompoundTree corpora in `corpora/trees`
- repository contains the two modules segmentation parser
  1. segmentation parser
  2. pcfg evaluation
- for more information about the modules see the `README.md` in the modules top level folder

---

# INSTALLATION

- compoundtree module is developed and tested on ubuntu 14.04
- programmed by using python 2.7.6
- install bitpar from: [bitpar project](http://www.cis.uni-muenchen.de/~schmid/tools/BitPar/)
- [evalb](http://nlp.cs.nyu.edu/evalb/) is already included in the `pcfg_evaluation` module
- installation: `pip install -e compoundtree/`

---

# DEMO

- go to script folder with `cd script/`
- use one of following scripts with `bash <scriptname>`
  1. `parse_segmented_nouns.sh` -> parse segmentend nouns into trees
  2. `evaluate_pcfg.sh` -> evaluate pcfg based parsing
  3. `clean.sh` -> clean genereated files

---

# CONTACT

mail: philipp.gawlik@googlemail.com
