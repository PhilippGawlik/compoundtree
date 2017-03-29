#!/usr/bin/python

import subprocess

from progress.bar import Bar
from sklearn.model_selection import KFold
import numpy as np

from pcfg import annotate
from bitpar import lexicon, prepare_bitpar_input, grammar, parse_list


def preprocess(config):
    ''' Prepare data structures:

        x: compound words
        y: trees
        compound_card: word cardinality of
            compound words
        full_corpus: rows of full corpus

    '''
    corpora = {
        'x': [],
        'y': [],
        'full_corpus': [],
        'compound_card': []
    }
    with open(config['filesystem']['full_corpus'], 'r') as f:
        if config['verbose']:
            bar = Bar('Preprocess corpus\t', max=len(open(
                config["filesystem"]['full_corpus']).readlines()))
        # full_corpusor every line in input
        for line in f:
            # clean line
            line = line
            line = line.strip()
            # split line by columns
            column = line.split('\t')
            # cast tree to list of (id, compound) pairs
            corpora['x'].append((column[0], column[3]))
            # cast tree to list of (id, tree) pairs
            corpora['y'].append((column[0], column[-1]))
            corpora['full_corpus'].append((column[0], column[-1]))
            # count number of subwords in compound
            card = column[3].count('#') + 1
            corpora['compound_card'].append(card)
            if config['verbose']:
                bar.next()
    if config['verbose']:
        bar.finish()
    f.close()
    corpora['x'] = np.array(corpora['x'])
    corpora['y'] = np.array(corpora['y'])
    corpora['compound_card'] = np.array(corpora['compound_card'])
    return corpora


def preprocess_helper(config):
    '''Initiate preprocessing of the corpora.'''
    # five_error = []
    # process base corpora
    corpora = preprocess(config)
    # annotate corpora
    corpora['anno_full_corpus'] = annotate.annotate_list(
        corpora['full_corpus'], config['default_config'],
        'Annotate corpus\t\t')
    # make lexicon
    lexicon.make_lexicon_from_list_helper(
        corpora['anno_full_corpus'],
        config['lexicon_config'])
    return corpora


def filename_helper(path, buf, name):
    '''Generate file path and name.'''
    return '{}{}_{}'.format(path, buf, name)


def filename_list_helper(buf, config):
    '''Generate path and filename for:

        gold file
        grammar (for bitpar)
        input (for input)
        predictions (bitpar output)
        cleaned predictions

    '''
    files = {}
    for prefix in config['process_name_list']:
        files[prefix] = (filename_helper(
            config['filesystem'][prefix + '_file_path'],
            buf,
            config['filesystem'][prefix + '_file']))
    config['grammar_config']['output'] = files['grammar']
    config['bitpar_input_prepare_config']['output'] = files['bitpar_input']
    config['bitpar_input_config']['output'] = files['prediction']
    config['bitpar_input_config']['input'] = files['bitpar_input']
    config['bitpar_input_config']['grammar'] = files['grammar']
    config['gold_output_path'] = files['gold']
    config['cleaned_prediction'] = files['cleaned_prediction']
    config['analysis'] = files['analysis']


def write_gold_file(config, fold_corpora):
    '''Write gold standard trees to file.'''
    f = open(config['gold_output_path'], 'w')
    for (_, tree) in fold_corpora['gold']:
        f.write('{}\n'.format(tree.decode('utf-8').encode('latin-1')))
    f.close()


def preprocess_fold(corpora, train_idx, test_idx, config, buf):
    '''Preprocess data necessary for processing a fold:

        1. generate file names
        2. train corpus
        3. bitpar input
        4. gold standard corpus
        5. annotate train/ test corpus

    '''
    fold_corpora = {}
    # generate filnames
    filename_list_helper(buf, config)
    # generate corpora
    fold_corpora['train_trees'] = corpora['y'][train_idx]
    fold_corpora['bitpar_input'] = corpora['y'][test_idx]
    if config['make_gold']:
        fold_corpora['gold'] = corpora['y'][test_idx]
        write_gold_file(config, fold_corpora)
    fold_corpora['anno_train_trees'] = annotate.annotate_list(
        fold_corpora['train_trees'],
        config['default_config'],
        'Annotate train corpus\t')
    fold_corpora['anno_bitpar_input'] = annotate.annotate_list(
        fold_corpora['bitpar_input'],
        config['default_config'],
        'Annotate test corpus\t')
    return fold_corpora


def clean_predictions(config):
    '''Clean predictions from bitpar specific output symbols
       to fit the gold standard trees.
    '''
    # clean from head annotation and from symbols the bitar parser inserted
    pred_file = open(config['cleaned_prediction'], 'w')
    sed1 = subprocess.Popen((
        'sed', 's/\/\w*//g',
        config['bitpar_input_config']['output']),
        stdout=subprocess.PIPE)
    sed2 = subprocess.Popen(
        ('sed', 's/(top (car \\\^)(top_end //g'),
        stdin=sed1.stdout, stdout=subprocess.PIPE)
    sed3 = subprocess.Popen(
        ('sed', 's/(dol \\\$)))//g'),
        stdin=sed2.stdout, stdout=subprocess.PIPE)
    sed4 = subprocess.Popen(
        ('sed', 's/\\\^/\^/g'), stdin=sed3.stdout, stdout=subprocess.PIPE)
    sed5 = subprocess.Popen(
        ('sed', 's/\\\$/\$/g'), stdin=sed4.stdout, stdout=pred_file)
    sed5.wait()
    pred_file.flush()
    pred_file.close()


def evaluate(config):
    '''Use evalb to compare the parsed trees to the gold standard trees.'''
    if config['verbose']:
        print 'Evaluate'
    ana_file = open(config['analysis'], 'w')
    evalb = subprocess.Popen((
        config['evalb']['path'],
        '-p',
        config['evalb']['prm_path'],
        config['gold_output_path'],
        config['cleaned_prediction']),
        stdout=ana_file)
    evalb.wait()
    ana_file.flush()
    ana_file.close()


def pipeline(config):
    '''Process pipeline that:

        1. preprocesses corpora
        2. runs kfold on corpora that
            3. prepare gold, train, test trees
            4. generate PCFG
            5. parse test corpus
            6. evaluate results

    '''
    # 1. preprocesses corpora
    corpora = preprocess_helper(config)
    # 2. run kfold on corpora that
    buf = 1
    kf = KFold(n_splits=config['folds'])
    for train_idx, test_idx in kf.split(corpora['x']):
        if config['verbose']:
            print '\nMake {}. fold'.format(buf)
        fold_corpora = preprocess_fold(
            corpora, train_idx, test_idx, config, buf)
        # generate PCFG
        grammar.make_grammar_from_list_helper(
            fold_corpora['anno_train_trees'], config['grammar_config'])
        # prepare bitpar input
        prepare_bitpar_input.make_input_from_list_helper(
            fold_corpora['anno_bitpar_input'],
            config['bitpar_input_prepare_config'])
        # parse test corpus with bitpar
        parse_list.run_helper(config['bitpar_input_config'])
        # clean predictions from bitpar specific symbols
        clean_predictions(config)
        # generate evalb evaluation
        evaluate(config)
        if config['verbose']:
            print 'Done with fold {}'.format(buf)
        # raise fold buffer
        buf += 1
