# -*- coding: utf-8 -*-
'''Define file encoding.'''
#######################################################
# name: lexicon.py
# author: Philipp Gawlik
# date: (Mi 01 March 2017 13:52:36 CET)
# purpose: Extract a bitpar compatible grammar from corpus.
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
        default='grammar.bitpar',
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


def write_grammar(
        (unary_rules, binary_rules, total_count),
        out_file,
        to_screen=False):
    '''Write grammar to file.'''
    if to_screen:
        for (lhs, rhs_dict) in sorted(unary_rules.iteritems()):
            for (rhs, count) in sorted(rhs_dict.iteritems()):
                print '{} {} {}'.format(
                    count, lhs, rhs).decode('utf-8').encode('latin-1')
        for (lhs, rhs_dict) in sorted(binary_rules.iteritems()):
            for ((lrhs, rrhs), count) in sorted(rhs_dict.iteritems()):
                print '{} {} {} {}'.format(
                    count, lhs, lrhs, rrhs).decode('utf-8').encode('latin-1')
    else:
        out_file = open(out_file, 'w')
        for (lhs, rhs_dict) in sorted(unary_rules.iteritems()):
            for (rhs, count) in sorted(rhs_dict.iteritems()):
                out_file.write('{} {} {}\n'.format(
                    count, lhs, rhs).decode('utf-8').encode('latin-1'))
        for (lhs, rhs_dict) in sorted(binary_rules.iteritems()):
            for ((lrhs, rrhs), count) in sorted(rhs_dict.iteritems()):
                out_file.write('{} {} {} {}\n'.format(
                    count, lhs, lrhs, rrhs).decode('utf-8').encode('latin-1'))
        out_file.close()


def add_total_count(total_count, lhs):
    '''Count occurence of a rule with specific left hand side.'''
    # if left hand side is known
    if lhs in total_count:
        total_count[lhs] += 1
    # otherwise
    else:
        total_count[lhs] = 1
    return total_count


def add_unary_rule((unary_rules, binary_rules, total_count), lhs, rhs):
    '''Count a unary rule in the grammar.'''
    # if rule is already known
    if lhs in unary_rules:
        rhs_dict = unary_rules[lhs]
        if rhs in rhs_dict:
            rhs_dict[rhs] += 1
        else:
            rhs_dict[rhs] = 1
    # add new rule to grammar
    else:
        unary_rules[lhs] = {rhs: 1}
    # count rule
    total_count = add_total_count(total_count, lhs)
    return (unary_rules, binary_rules, total_count)


def add_binary_rule((unary_rules, binary_rules, total_count), lhs, rhs):
    '''Count a binary rule in the grammar.'''
    # if rule is already known
    if lhs in binary_rules:
        rhs_dict = binary_rules[lhs]
        if rhs in rhs_dict:
            rhs_dict[rhs] += 1
        else:
            rhs_dict[rhs] = 1
    # add new rule to grammar
    else:
        binary_rules[lhs] = {rhs: 1}
    # count rule
    total_count = add_total_count(total_count, lhs)
    return (unary_rules, binary_rules, total_count)


def unary(tree, tree_id, grammar):
    '''Extract rules from unary branches.'''
    [lhs, rhs] = tree
    # if leaf is reached
    if type(rhs) == str:
        # leafs and their base label are accounted in the lexicon
        return grammar
    # follow unary branch towards leaf
    elif type(rhs) == list:
        # count rule
        grammar = add_unary_rule(grammar, lhs, rhs[0])
        return unary(rhs, tree_id, grammar)
    # found structural error
    else:
        print 'Found structural error in tree {}'.format(tree_id)
        return grammar


def count_rules(tree, tree_id, grammar):
    ''' Extract list with (word, word_category) tuples.'''
    # base case: unary branch
    if len(tree) == 2:
        return unary(tree, tree_id, grammar)
    # step case: binary branch
    elif len(tree) == 3:
        [lhs, rlhs, rrhs] = tree
        if type(rlhs) != list or type(rrhs) != list:
            print 'Found error in tree {}'.format(tree_id)
            return grammar
        grammar = add_binary_rule(grammar, lhs, (rlhs[0], rrhs[0]))
        # left branch
        grammar = count_rules(rlhs, tree_id, grammar)
        # right branch
        grammar = count_rules(rrhs, tree_id, grammar)
        return grammar
    # found structural error
    else:
        print 'Found structural error in tree: {}'.format(tree_id)
        return grammar


def extract_grammar(input_file, verbose=False):
    ''' Extract dict with lhs to (rhs, count) mapping
        of the grammar rules.

        { "lhs" : {
            "rhs1": "rule_count",
            "rhs2": "rule_count",
            .....
            }
        ...
        }

        The rule dicts a separated into one dict for unary
        and one dict for binary rules.

        Furthermore a dict is generated to keep the total
        count of lhs rules. The mapping is as follows:

        { "lhs" : "lhs_count" }

    '''
    unary_rules = {}
    binary_rules = {}
    total_count = {}
    # setup grammar
    grammar = (unary_rules, binary_rules, total_count)
    if verbose:
        num_lines = sum(1 for line in open(input_file))
        bar = Bar('Processing', max=num_lines)
    with open(input_file, 'r') as f:
        # for every tree
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
            # extract rules and their count from trees
            grammar = count_rules(tree, tree_id, grammar)
            if verbose:
                bar.next()
        if verbose:
            bar.finish()
        f.close()
    return grammar


def extract_grammar_from_list(train_trees, verbose=False):
    ''' Extract dict with lhs to (rhs, count) mapping
        of the grammar rules.

        { "lhs" : {
            "rhs1": "rule_count",
            "rhs2": "rule_count",
            .....
            }
        ...
        }

        The rule dicts a separated into one dict for unary
        and one dict for binary rules.

        Furthermore a dict is generated to keep the total
        count of lhs rules. The mapping is as follows:

        { "lhs" : "lhs_count" }

    '''
    unary_rules = {}
    binary_rules = {}
    total_count = {}
    # setup grammar
    grammar = (unary_rules, binary_rules, total_count)
    if verbose:
        bar = Bar('Generate PCFG\t\t', max=len(train_trees))
    # for every tree
    for (tree_id, tree) in train_trees:
        # get tree
        tree = tree_string_to_list(tree)
        # extract rules and their count from trees
        grammar = count_rules(tree, tree_id, grammar)
        if verbose:
            bar.next()
    if verbose:
        bar.finish()
    return grammar


def make_grammar_helper(config):
    '''Make a grammar from a tree corpus.'''
    # extract grammar from input file
    grammar = extract_grammar(config['input'], config['verbose'])
    # write grammar to file
    write_grammar(grammar, config['output'])


def make_grammar_from_list_helper(train_trees, config):
    '''Make a grammar from a tree corpus.'''
    # extract grammar from input file
    grammar = extract_grammar_from_list(train_trees, config['verbose'])
    # write grammar to file
    write_grammar(grammar, config['output'])


def make_grammar():
    '''Make a grammar from a tree corpus.'''
    arg_parser = build_arg_parse()
    args = arg_parser.parse_args()
    config = make_config(args)
    make_grammar_helper(config)


if __name__ == '__main__':
    make_grammar()
