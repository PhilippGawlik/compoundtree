# -*- coding: utf-8 -*-
'''Define file encoding.'''
#######################################################
# name: lexicon.py
# author: Philipp Gawlik
# date: (Mi 01 March 2017 13:52:36 CET)
# purpose: Extract a bitpar compatible lexicon from corpus.
######################################################

import sys
import argparse

from progress.bar import Bar
from pyparsing import nestedExpr


def build_arg_parse():
    '''Build a command line parser.'''
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input',
        dest='input',
        type=str,
        default=None,
        help='Location of input file.')
    parser.add_argument(
        '--output',
        dest='output',
        type=str,
        default='lexicon.bitpar',
        help='Location of output file.')
    parser.add_argument(
        '--verbose',
        dest='verbose',
        action='store_true',
        default=False,
        help='set to generate process information')
    return parser


def make_config(args):
    '''Transform command line arguments into config dict.'''
    return {
        'input': args.input,
        'output': args.output,
        'verbose': args.verbose
        }


def tree_string_to_list(tree):
    '''Parse tree string to list.'''
    parse_input = '({})'.format(tree)
    try:
        out = nestedExpr().parseString(parse_input).asList()[0][0]
    except:
        print tree
        sys.exit()
    return out


def cat_dict_to_str(cat_dict):
    '''Transform a dict of tuples:

       (string, int)

       to a printable list.
    '''
    str_ls = ''
    for (cat, card) in cat_dict.iteritems():
        str_ls += '\t{} {}'.format(cat, card)
    return str_ls


def write_lex(lex, out_file, to_screen=False):
    '''Write lexicon to file or screen.'''
    if to_screen:
        for (word, cat_dict) in sorted(lex.iteritems()):
            print '{}{}'.format(
                word, cat_dict_to_str(cat_dict)
                ).decode('utf-8').encode('latin-1')
    else:
        out_file = open(out_file, 'w')
        for (word, cat_dict) in sorted(lex.iteritems()):
            out_file.write('{}{}\n'.format(
                word, cat_dict_to_str(cat_dict)
                ).decode('utf-8').encode('latin-1'))
        out_file.close()


def unary(tree, tree_id):
    '''Process unary terminal tree.'''
    head = tree.pop(0)
    rest = tree[0]
    # found word
    if type(rest) == str:
        return [(rest, head)]
    # follow branch in leaf direction
    elif type(rest) == list:
        return unary(rest, tree_id)
    # error in tree structure
    else:
        print 'Found structural error in tree {}'.format(tree_id)
        return [('', '')]


def extract_words(tree, tree_id):
    ''' Extract list with (word, word_category) tuples
        in a recursive manner.
    '''
    # base case: unary branch
    if len(tree) == 2:
        return unary(tree, tree_id)
    # step case: binary branch
    elif len(tree) == 3:
        [head, lhs, rhs] = tree
        # found a structural error
        if type(rhs) != list or type(lhs) != list:
            print 'Found error in tree {}'.format(tree_id)
            return []
        # follow left branch towards leaf
        words_left = extract_words(lhs, tree_id)
        # follow right branch towards leaf
        words_right = extract_words(rhs, tree_id)
        words_left.extend(words_right)
        return words_left
    else:
        print 'Found structural error in tree: {}'.format(tree_id)


def extract_lexicon(input_file, verbose=False):
    ''' Extract dict with word to word_category
        and word occurence mapping from tree.

        { "word1" : {
            "cat_name1": "cat_cardinality",
            "cat_name2": "cat_cardinality",
            .....
            }
        ...
        }
    '''
    lex = {}
    if verbose:
        num_lines = sum(1 for line in open(input_file))
        bar = Bar('Processing', max=num_lines)
    with open(input_file, 'r') as f:
        # for every tree
        for line in f:
            line = line.decode('latin-1').encode('utf-8')
            # clean line
            line = line.strip()
            # split line by columns
            column = line.split('\t')
            # get tree id for error reports
            tree_id = column[0]
            # get tree
            tree = tree_string_to_list(column[-1])
            # extract words from leafes of the tree
            words = extract_words(tree, tree_id)
            # count word occurences
            for (word, cat) in words:
                # increase word count
                if word in lex:
                    cat_dict = lex[word]
                    if cat in cat_dict:
                        cat_dict[cat] += 1
                    else:
                        cat_dict[cat] = 1
                # add unseen word
                else:
                    lex[word] = {cat: 1}
            if verbose:
                bar.next()
        if verbose:
            bar.finish()
        f.close()
    return lex


def extract_lexicon_from_list(full_corpus, verbose=False):
    ''' Extract dict with word to word_category
        and word occurence mapping from tree.

        { "word1" : {
            "cat_name1": "cat_cardinality",
            "cat_name2": "cat_cardinality",
            .....
            }
        ...
        }
    '''
    lex = {}
    if verbose:
        bar = Bar('Generate bitpar lexicon\t', max=len(full_corpus))
    for (tree_id, tree) in full_corpus:
        tree = tree_string_to_list(tree)
        # extract words from leafes of the tree
        words = extract_words(tree, tree_id)
        # count word occurences
        for (word, cat) in words:
            # increase word count
            if word in lex:
                cat_dict = lex[word]
                if cat in cat_dict:
                    cat_dict[cat] += 1
                else:
                    cat_dict[cat] = 1
            # add unseen word
            else:
                lex[word] = {cat: 1}
        if verbose:
            bar.next()
    if verbose:
        bar.finish()
    return lex


def make_lexicon_from_list_helper(full_corpus, config):
    '''Make a word lexicon from a tree corpus.'''
    # extract lexicon from input file
    lex = extract_lexicon_from_list(full_corpus, config['verbose'])
    # write lexicon to file
    write_lex(lex, config['output'])


def make_lexicon_helper(config):
    '''Make a word lexicon from a tree corpus.'''
    if config['verbose']:
        print 'Process bitpar lexicon'
    # extract lexicon from input file
    lex = extract_lexicon(config['input'], config['verbose'])
    # write lexicon to file
    write_lex(lex, config['output'])


def make_lexicon(config={}):
    '''Make a word lexicon from a tree corpus.'''
    arg_parser = build_arg_parse()
    args = arg_parser.parse_args()
    config = make_config(args)
    make_lexicon_helper(config)


if __name__ == '__main__':
    make_lexicon()
