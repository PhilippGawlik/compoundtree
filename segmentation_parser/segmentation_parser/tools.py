# -*- coding: utf-8 -*-
'''Define file encoding.'''
#######################################################
# name: tools.py
# author: Philipp Gawlik
# date: (Mi 01 Mar 2017 19:36:43 CET)
# purpose: Some helper functions for parsing compound
# nouns into tree structures.
######################################################

import re


def unsplit_compound(compound):
    '''Remove split markers from compound noun
       to restore original word.'''
    comp_restored = compound
    comp_restored = comp_restored.replace('#', '')
    comp_restored = re.sub(r'\\', '', comp_restored)
    comp_restored = re.sub(r'<..?.?>', '', comp_restored)
    comp_restored = comp_restored.replace('~', '')
    comp_restored = comp_restored.replace('|', '')
    comp_restored = comp_restored.replace('@', '')
    comp_restored = comp_restored.replace('=', '')
    return comp_restored


def read_from_file(path):
    ''' Read compound nouns line wise form input file.'''
    comp_nouns = []
    with open(path, 'r') as f:
        for (idx, line) in enumerate(f, start=1):
            # clean each line
            line = line.decode('latin-1').encode('utf-8')
            line = line.strip()
            # if line is marked as comment ignore it
            if line[0] != '#':
                comp_nouns.append((idx, line))
        f.close()
    return comp_nouns


def write_results(pairs, out_file):
    ''' Write rows of:

        - id
        - tree_idx
        - compound noun
        - weight
        - analyzed compound noun
        - tree

        Row format follows Wuerzner and Hanneforth (2006).
    '''
    out_file = open(out_file, 'w')
    for (idx, compound_noun, tree_list) in pairs:
        word = unsplit_compound(compound_noun)
        for (tree_idx, tree) in enumerate(tree_list, 1):
            out_str = '{}_{}\t{}\t{}\t{}\t{}\n'.format(
                str(idx),
                str(tree_idx),
                word,
                '<0.0>',
                compound_noun,
                tree)
            out_file.write(out_str)
    out_file.close()
