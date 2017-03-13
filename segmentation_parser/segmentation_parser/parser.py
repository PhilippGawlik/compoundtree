# -*- coding: utf-8 -*-
'''Define file encoding.'''
#######################################################
# name: parser.py
# author: (philipp)
# date: (Mi 01 Mar 2017 19:36:43 CET)
# purpose: Parse analyzed compound nouns to provide
# a syntactic tree.
######################################################

from concurrent.futures import ProcessPoolExecutor
import argparse

from progress.bar import Bar
import dot_write
import tools
import tree_generator
import grammar.grammar as grammar

DOT_DIR = '../../corpora/dot/'
DEFAULT_IN = '../../corpora/segments/compound_cleaned_random.txt'
DEFAULT_OUT = '../../corpora/trees/seg_parser.out'


def build_arg_parse():
    '''Build a command line parser.'''
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--out',
        dest='output',
        type=str,
        default=DEFAULT_OUT,
        help='specify file holding the output')
    parser.add_argument(
        '--in',
        dest='input',
        type=str,
        default=DEFAULT_IN,
        help='specify file holding the input')
    parser.add_argument(
        '--verbose',
        dest='verbose',
        action='store_true',
        default=False,
        help='set to generate process information')
    parser.add_argument(
        '--dot',
        dest='dot',
        action='store_true',
        default=False,
        help='set to generate dot file for each word')
    parser.add_argument(
        '--dot-dir',
        dest='dot_dir',
        type=str,
        default=DOT_DIR,
        help='set dot file output path')
    parser.add_argument(
        '--max-workers',
        dest='max_workers',
        type=int,
        default=1,
        help='set number of prallel workers (cores)')
    return parser


def parse((idx, comp_noun)):
    ''' Parse a compound noun in 2 steps:

        1. Parse the morphs of the compound into a list
           of POS rooted unary terminal trees

        2. Generate a list of binary tree variants that
           premutate left, right and central branching.

    '''
    # parse list of unary terminal trees
    result_list = grammar.compound.parseString(comp_noun)
    if result_list:
        # build a list of possible binary trees from unary
        # terminal trees
        tree_list = tree_generator.generate(result_list)
        if tree_list:
            return (idx, comp_noun, tree_list)
    print 'Problems with: {} while parsing'.format(comp_noun)
    return (idx, comp_noun, ['error'])


def parallel_parse_helper(comp_nouns, max_workers, bar, verbose=False):
    ''' Parse compound nouns in parallel.
        "max_workers" specifies number of parallel processes.
    '''
    results = []
    # generate list of syntax trees for each compound noun
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        for comp_noun_tuple in executor.map(parse, comp_nouns):
            results.append(comp_noun_tuple)
            if verbose:
                bar.next()
    return (results, bar)


def run():
    '''Wrapper function.'''
    # parse command line arguments
    arg_parser = build_arg_parse()
    args = arg_parser.parse_args()
    # get output file path
    output_loc = args.output
    # read in compound noun list
    comp_nouns = tools.read_from_file(args.input)
    if comp_nouns:
        # show process bar
        if args.verbose:
            print 'Segmented Compound Noun Parser Version 1.0'
            bar = Bar('Parse nouns\t', max=len(comp_nouns))
        (results, bar) = parallel_parse_helper(
            comp_nouns, args.max_workers, bar, args.verbose)
        if args.verbose:
            bar.finish()
        # write results to file
        if args.verbose:
            print 'Writing parse results to {}'.format(output_loc)
        if results:
            tools.write_results(results, output_loc)
            # write dot file
            if args.dot:
                dot_write.write(results, args.dot_dir, args.verbose)


if __name__ == '__main__':
    run()
