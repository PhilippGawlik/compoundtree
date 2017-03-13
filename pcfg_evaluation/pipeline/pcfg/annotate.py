# -*- coding: utf-8 -*-
'''Define file encoding.'''
#######################################################
# name: grammar.py
# author: Philipp Gawlik
# date: (Mi 01 Mar 2017 19:36:43 CET)
# purpose: Grammar for parse a morphological analysed
# compound nouns in list representation into a
# list of unary terminal trees.
######################################################

import sys
import argparse

from progress.bar import Bar
from pyparsing import nestedExpr

ROOT = 'root'


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
        default='out.txt',
        help='Location of output file.')
    parser.add_argument(
        '--parent',
        dest='parent',
        action='store_true',
        default=False,
        help='Enable parent annotation.')
    parser.add_argument(
        '--top',
        dest='top',
        action='store_true',
        default=False,
        help='Add a top node to root of the tree.')
    parser.add_argument(
        '--lexem',
        dest='lex',
        action='store_true',
        default=False,
        help='Enable lexicalization of the pcfg.')
    parser.add_argument(
        '--head',
        dest='head',
        action='store_true',
        default=False,
        help='Enable head annotation.')
    parser.add_argument(
        '--verbose',
        dest='verbose',
        action='store_true',
        default=False,
        help='set to generate process information')
    return parser


def return_test():
    return 'anno_test'


def make_config(args):
    '''Transform command line arguments into config dict.'''
    return {
        'input': args.input,
        'output': args.output,
        'parent': args.parent,
        'top': args.top,
        'lex': args.lex,
        'head': args.head,
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


def tree_list_to_string(tree):
    '''Parse tree list to bracketed string.'''
    # base case not nested tree
    temp_ls = []
    for elem in tree:
        temp_ls.append(
            tree_list_to_string(
                elem)) if type(elem) == list else temp_ls.append(elem)
    return '({})'.format(' '.join(temp_ls))


def cat_dict_to_str(cat_dict):
    '''Transform a dict of tuples:

       (string, int)

       to a printable list.
    '''
    str_ls = ''
    for (cat, card) in cat_dict.iteritems():
        str_ls += '\t{} {}'.format(cat, card)
    return str_ls


def write_content(
        file_content,
        out_file,
        to_screen=False):
    '''Output annoatated file content.'''
    if to_screen:
        for line in file_content:
            print '\t'.join(line).decode('utf-8').encode('latin-1')
    else:
        out_file = open(out_file, 'w')
        for line in file_content:
            out_file.write('\t'.join(line).decode('utf-8').encode('latin-1'))
            out_file.write('\n')
        out_file.close()


def add_top_node(tree, tree_id):
    '''Add a top node as well as beginning and end marker.

                    top
                   /   \
                  /     \
                car   top_end
                 |     /   \
                 |    /     \
                 ^  tree    dol
                    ...      |
                             |
                             $
    '''
    return ['top', ['car', '^'], ['top_end', tree, ['dol', '$']]]


def annotate_node(label, parent, head, lex, config, terminal=False):
    ''' Annotate node label with head, parent and lexem.

        Follow Johnson (1998) the root note is spared from
        the parent annotation as well as the base node (one
        above the terminal). To ensure that, an extra
        argument of the function checks, if current node
        is root node.

        Following Johnson (1998) the base node that is
        one node above the terminal should be spared
        from the annotation.
    '''
    if config['parent'] and parent != 'root' and not terminal:
        label += '/{}'.format(parent)
    if config['head'] and parent != 'root' and not terminal:
        label += '/{}'.format(head)
    if config['lex'] and parent != 'root':
        label += '/{}'.format(lex)
    return label


def unary(tree, parent, config, tree_id):
    ''' Annotate a unary branching note with
        head, parent and lexem annotation.'''
    [lhs, rhs] = tree
    if type(rhs) == list:
        next_parent = lhs
        (tree, head, lex) = unary(rhs, next_parent, config, tree_id)
        anno_lhs = annotate_node(lhs, parent, head, lex, config)
        return ([anno_lhs, tree], head, lex)
    if type(rhs) == str:
        if config['lex']:
            lhs = annotate_node(lhs, '', '', rhs, config, True)
        return ([lhs, rhs], lhs, rhs)
    else:
        print 'Found structural error in tree {}'.format(tree_id)
        return ([], '')


def binary(tree, parent, config, tree_id):
    ''' Annotate a binary branching note with
        head, parent and lexem annotation.'''
    if len(tree) == 2:
        return unary(tree, parent, config, tree_id)
    elif len(tree) == 3:
        [lhs, rlhs, rrhs] = tree
        next_parent = lhs
        # in german morphology the head is always on the right
        # see Eisenberg for more information
        (ltree, _, _) = binary(rlhs, next_parent, config, tree_id)
        (rtree, head, lex) = binary(rrhs, next_parent, config, tree_id)
        anno_lhs = annotate_node(lhs, parent, head, lex, config)
        return ([anno_lhs, ltree, rtree], head, lex)
    else:
        print 'Found structural error in tree: {}'.format(tree_id)
        return ([], '')


def annotate_list(full_corpus, config, proc_msg='process', root=ROOT):
    ''' Annotate the trees with top, parent of head and
        lexicalize the trees.'''
    anno_full_corpus = []
    # for every line in input
    if config['verbose']:
        bar = Bar(proc_msg, max=len(full_corpus))
    for (tree_id, tree) in full_corpus:
        # cast tree to list
        tree_ls = tree_string_to_list(tree)
        # get tree id for error reports
        if config['top']:
            # perform top annotation
            tree_ls = add_top_node(tree_ls, tree_id)
        if config['parent'] or config['lex'] or config['head']:
            # perform parent, head and lex annotation
            (tree_ls, _, _) = binary(tree_ls, 'root', config, tree_id)
        # cast tree list to string
        tree = tree_list_to_string(tree_ls)
        # put tree back into row
        anno_full_corpus.append((tree_id, tree))
        if config['verbose']:
            bar.next()
    if config['verbose']:
        bar.finish()
    return anno_full_corpus


def annotate_helper(config, root=ROOT):
    ''' Annotate the trees with top, parent of head and
        lexicalize the trees.'''
    # to collect trees
    lines = []
    if config['verbose']:
        num_lines = sum(1 for line in open(config['input']))
        bar = Bar('Processing', max=num_lines)
    with open(config['input'], 'r') as f:
        # for every line in input
        for line in f:
            # clean line
            line = line.decode('latin-1').encode('utf-8')
            line = line.strip()
            # split line by columns
            column = line.split('\t')
            # cast tree to list
            tree_ls = tree_string_to_list(column[-1])
            # get tree id for error reports
            tree_id = column[0]
            if config['top']:
                # perform top annotation
                tree_ls = add_top_node(tree_ls, tree_id)
            if config['parent'] or config['lex'] or config['head']:
                # perform parent, head and lex annotation
                (tree_ls, _, _) = binary(tree_ls, 'root', config, tree_id)
            # cast tree list to string
            tree_str = tree_list_to_string(tree_ls)
            # put tree back into row
            column[-1] = tree_str
            lines.append(column)
            if config['verbose']:
                bar.next()
        if config['verbose']:
            bar.finish()
        f.close()
    return lines


def annotate(config):
    '''Make a word lexicon from a tree corpus.'''
    # annotate the trees
    annotated_content = annotate_helper(config)
    # write trees to file
    write_content(annotated_content, config['output'])


def run():
    '''Make a word lexicon from a tree corpus.'''
    arg_parser = build_arg_parse()
    args = arg_parser.parse_args()
    config = make_config(args)
    annotate(config)


if __name__ == '__main__':
    run()
