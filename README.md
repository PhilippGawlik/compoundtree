Compoundtree Version 1.0; 2017

# GENERAL

- find CompoundTree corpora in `corpora/trees`
- repository contains the two modules segmentation parser
  1. segmentation parser
  2. pcfg evaluation
- for more information about the modules see the `README.md` in the modules top level folder

---

# INSTALLATION

- see `requirements.txt` for used third-party packages (we recommend to use virtualenv and pip for installation)
- perform the following steps:
  1. virtualenv .env
  2. source .env/bin/activate
  3. pip install -r requirements.txt
- programmed by using python 2.7.6

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
