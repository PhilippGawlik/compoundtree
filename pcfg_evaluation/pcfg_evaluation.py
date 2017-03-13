#!/usr/bin/python

import time
import json
import argparse

import pipeline.pipeline as pipeline


def build_arg_parse():
    '''Build a command line parser.'''
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--config-path',
        dest='config_path',
        type=str,
        default='../etc/config.json',
        help='Path to the config file.')
    parser.add_argument(
        '--verbose',
        dest='verbose',
        action='store_true',
        default=False,
        help='Ouput process information.')
    parser.add_argument(
        '--parent',
        dest='parent',
        action='store_true',
        default=False,
        help='Enable parent annotation.')
    parser.add_argument(
        '--lex',
        dest='lex',
        action='store_true',
        default=False,
        help='Enable lex annotation.')
    parser.add_argument(
        '--head',
        dest='head',
        action='store_true',
        default=False,
        help='Enable head annoation.')
    parser.add_argument(
        '--no-gold',
        dest='no_gold',
        action='store_true',
        default=False,
        help="Don't write new gold standard files (if old files in use).")
    parser.add_argument(
        '--folds',
        dest='folds',
        type=int,
        default=4,
        help='Specify number of folds.')
    return parser


def make_config(args):
    '''Load default config and adjust values with command line input.'''
    # load default config file
    with open(args.config_path, 'r') as handle:
        config = json.load(handle)
    config['folds'] = args.folds
    config['verbose'] = args.verbose
    config['default_config']['verbose'] = args.verbose
    config['lexicon_config']['verbose'] = args.verbose
    config['grammar_config']['verbose'] = args.verbose
    config['bitpar_input_prepare_config']['verbose'] = args.verbose
    config['bitpar_input_config']['verbose'] = args.verbose
    config['default_config']['parent'] = args.parent
    config['default_config']['head'] = args.head
    config['default_config']['lex'] = args.lex
    config['make_gold'] = True if not args.no_gold else False
    return config


def get_schemes(config):
    '''Make a string with enabled annoatation schemes.'''
    schemes = []
    for key in ['parent', 'head', 'lex']:
        if config['default_config'][key]:
            schemes.append(key)
    return ', '.join(schemes) if schemes else 'none'


def print_header(config):
    '''Give an overview about process settings.'''
    print
    print 'Corpus: {}'.format(config['filesystem']['full_corpus'])
    print 'Annotation schemes: {}'.format(get_schemes(config))
    print 'Folds: {}'.format(config['folds'])
    print


def print_footer(start_time):
    '''Print some process information to screen.'''
    print 'Total time: {} seconds'.format(time.time() - start_time)


def pipeline_helper(start_time):
    '''Wrapper function.'''
    arg_parser = build_arg_parse()
    args = arg_parser.parse_args()
    config = make_config(args)
    if config['verbose']:
        print_header(config)
    pipeline.pipeline(config)
    if config['verbose']:
        print_footer(start_time)


if __name__ == '__main__':
    START_TIME = time.time()
    pipeline_helper(START_TIME)
