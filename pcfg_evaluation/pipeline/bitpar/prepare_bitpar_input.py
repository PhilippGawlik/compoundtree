# -*- coding: utf-8 -*-
'''Define file encoding.'''
#######################################################
# name: lexicon.py
# author: Philipp Gawlik
# date: (Mi 01 March 2017 13:52:36 CET)
# purpose: Prepare word input to fit bitpar input format.
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
        default='grammar',
        help='Location of input file.')
    parser.add_argument(
        '--output',
        dest='output',
        type=str,
        default='input.bitpar',
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


def write_word_list(word_list, out_file, to_screen=False):
    '''Write lexicon to file.'''
    if to_screen:
        for word in word_list:
            prefix = word.pop(0)
            out_str = prefix.decode('utf-8').encode('latin-1')
            for morph in word:
                out_str += ' {}'.format(
                    morph.decode('utf-8').encode('latin-1'))
            print out_str
    else:
        out_file = open(out_file, 'w')
        for word in word_list:
            prefix = word.pop(0)
            out_file.write(prefix.decode('utf-8').encode('latin-1'))
            for morph in word:
                out_file.write(' {}'.format(
                    morph.decode('utf-8').encode('latin-1')))
            out_file.write('\n')
        out_file.close()

def unary(tree, tree_id):
    '''Extract word.'''
    [head, rest] = tree
    # found word
    if type(rest) == str:
        return [rest]
    # follow branch to leaf
    elif type(rest) == list:
        return unary(rest, tree_id)
    # found structural error
    else:
        print 'Found structural error in tree {}'.format(tree_id)
        return ['']


def extract_word(tree, tree_id):
    ''' Extract list with splitted word parts.'''
    # base case: unary branch
    if len(tree) == 2:
        return unary(tree, tree_id)
    # step case: binary branch
    elif len(tree) == 3:
        [head, lhs, rhs] = tree
        if type(rhs) != list or type(lhs) != list:
            print 'Found error in tree {}'.format(tree_id)
            return []
        # left branch
        word_left = extract_word(lhs, tree_id)
        # right branch
        word_right = extract_word(rhs, tree_id)
        # collect words (leafs) of the trees in one list
        word_left.extend(word_right)
        return word_left
    else:
        print 'Found structural error in tree: {}'.format(tree_id)


def extract_word_list(input_file, verbose=False):
    ''' Extract splitted list of compound words
        from the tree in the input file.

        [
         [parts, of, word, one],
         [parts, of, word, two],
         ....
        ]
    '''
    word_list = []
    if verbose:
        num_lines = sum(1 for line in open(input_file))
        bar = Bar('Processing', max=num_lines)
    with open(input_file, 'r') as f:
        for line in f:
            # clean line
            line = line.decode('latin-1').encode('utf-8')
            line = line.strip()
            # split line by columns
            column = line.split('\t')
            # get tree id for error reports
            tree_id = column[0]
            # get tree
            tree = tree_string_to_list(column[-1])
            # add word to word list
            word_list.append(extract_word(tree, tree_id))
            if verbose:
                bar.next()
        if verbose:
            bar.finish()
        f.close()
    return word_list


def extract_word_list_from_list(bitpar_input, verbose=False):
    ''' Extract splitted list of compound words
        from the tree in the input file.

        [
         [parts, of, word, one],
         [parts, of, word, two],
         ....
        ]
    '''
    word_list = []
    if verbose:
        bar = Bar('Prepare bitpar input\t', max=len(bitpar_input))
    for (tree_id, tree) in bitpar_input:
        tree = tree_string_to_list(tree)
        # add word to word list
        word_list.append(extract_word(tree, tree_id))
        if verbose:
            bar.next()
    if verbose:
        bar.finish()
    return word_list


def make_input_helper(config):
    '''Make a splited compound word list.'''
    if config['verbose']:
        print 'Format bitpar input'
    word_list = extract_word_list(config['input'], config['verbose'])
    write_word_list(word_list, config['output'])


def make_input_from_list_helper(bitpar_input, config):
    '''Make a splited compound word list.'''
    word_list = extract_word_list_from_list(bitpar_input, config['verbose'])
    write_word_list(word_list, config['output'])


def make_input():
    '''Make a splited compound word list.'''
    arg_parser = build_arg_parse()
    args = arg_parser.parse_args()
    config = make_config(args)
    make_input_helper(config)


if __name__ == '__main__':
    make_input()
