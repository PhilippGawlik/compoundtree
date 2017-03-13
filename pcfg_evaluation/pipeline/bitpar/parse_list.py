# -*- coding: utf-8 -*-
'''Define file encoding.'''
#######################################################
# name: parse_list.py
# author: Philipp Gawlik
# date: (Mi 01 March 2017 13:52:36 CET)
# purpose: Use bitpar to parse a list of compound words.
######################################################

import argparse
import os
from subprocess import Popen, PIPE
from progress.bar import Bar


def build_arg_parse():
    '''Build a command line parser.'''
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input',
        dest='input',
        type=str,
        default='input.bitpar',
        help='Location of input file.')
    parser.add_argument(
        '--output',
        dest='output',
        type=str,
        default='predictions.evalb',
        help='Location of output file.')
    parser.add_argument(
        '--verbose',
        dest='verbose',
        action='store_true',
        default=False,
        help='set to generate process information')
    parser.add_argument(
        '--grammar',
        dest='grammar',
        type=str,
        default='grammar.bitpar',
        help='Location of bitpar grammar.')
    parser.add_argument(
        '--lexicon',
        dest='lexicon',
        type=str,
        default='lexicon.bitpar',
        help='Location of bitpar lexicon.')
    parser.add_argument(
        '--open-class-tags',
        dest='oct',
        type=str,
        default='pipeline/bitpar/bitpar/open-class-tags',
        help='Location of open-class-tags file.')
    parser.add_argument(
        '--wordclass',
        dest='wordclass',
        type=str,
        default='pipeline/bitpar/bitpar/wordclass.txt',
        help='Location of wordclass file.')
    return parser


def make_config(args):
    '''Transform command line arguments into config dict.'''
    return {
        'input': args.input,
        'output': args.output,
        'verbose': args.verbose,
        'grammar': args.grammar,
        'lexicon': args.lexicon,
        'oct': args.oct,
        'wordclass': args.wordclass
        }


def clean(tree):
    ''' Remove some markup symbols bitpar is adding.
        This is necessary to fit the gold standard.
    '''
    tree = tree.replace('\=', '=')
    return tree


def write_predictions(predictions, out_file, to_screen=False):
    '''Write predictions to file.'''
    if to_screen:
        for tree in predictions:
                print '{}'.format(tree)
    else:
        out_file = open(out_file, 'w')
        for tree in predictions:
                out_file.write(
                    '{}'.format(tree.decode('utf-8').encode('latin-1')))
        out_file.close()


def parse_list(input_file, cmd, verbose=False):
    '''Use bitpar to parse a list of compound words.'''
    trees = []
    if verbose:
        num_lines = sum(1 for line in open(input_file))
        bar = Bar('Parse test corpus\t', max=num_lines)
    with open(input_file, 'r') as f:
        # for every tree
        for line in f:
            # clean line
            line = line.decode('latin-1').encode('utf-8')
            line = line.strip()
            # split line into morphs
            compound = line.split(' ')
            # bitpar input needs to be in specific format
            # and has to be from a file
            temp_file = "temp.txt"
            # generate file with input
            open(temp_file, "w").writelines(
                '{}\n\n'.format('\n'.join(compound)))
            # parse file with bitpar
            trees.append(clean(parse_word(temp_file, cmd)))
            if verbose:
                bar.next()
        if verbose:
            bar.finish()
        f.close()
        # remove temporary file
        os.remove(temp_file)
    return trees


def parse_word(temp_file, cmd):
    '''Parse single compound word form file.'''
    # open file holding input compound
    f = open(temp_file, 'r')
    # parsing compound with bitpar
    bitpar = Popen(cmd, stdin=f, stdout=PIPE, stderr=PIPE)
    # print bitpar.stderr.read()
    return bitpar.stdout.read()


def run_helper(config):
    '''Wrapper function.'''
    cmd = [
        'bitpar',
        '-ts',
        '()',
        '-s',
        'top',
        '-v',
        config['grammar'],
        config['lexicon'],
        '-u',
        config['oct'],
        '-w',
        config['wordclass'],
        ]
    predictions = parse_list(config['input'], cmd, config['verbose'])
    write_predictions(predictions, config['output'])


def run():
    '''Wrapper function.'''
    arg_parser = build_arg_parse()
    args = arg_parser.parse_args()
    config = make_config(args)
    run_helper(config)


if __name__ == '__main__':
    run()
