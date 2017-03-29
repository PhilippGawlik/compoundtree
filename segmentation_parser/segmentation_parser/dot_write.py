# -*- coding: utf-8 -*-
'''Define file encoding.'''

import sys
from progress.bar import Bar

import grammar.grammar as grammar


def write_node_definition(out_file, node_label, node_idx):
    '''Write node definition by associating
       the node label with a uniq index.'''
    node_idx += 1
    out_file.write('\t{} [label="{}"];\n'.format(node_idx, node_label))
    return node_idx


def write_terminal_definition(out_file, parent, terminal, node_idx):
    '''Write node definition by associating
       the node label with a uniq index.'''
    parent_idx = node_idx + 1
    out_file.write('\t{} [label="{}"];\n'.format(parent_idx, parent))
    terminal_idx = parent_idx + 1
    out_file.write('\t{} [label="{}"];\n'.format(terminal_idx, terminal))
    return (terminal_idx, parent_idx, terminal_idx)


def write_node(out_file, node_idx):
    '''Write a terminal node.'''
    out_file.write('\t{};\n'.format(node_idx))


def write_transition(out_file, parent_idx, child_idx):
    '''Write a transition'''
    out_file.write('\t{}->{};\n'.format(parent_idx, child_idx))


def rekursive_dot_write(out_file, parent_idx, children, node_idx):
    ''' Translate the levels of the tree
        to dot format in a rekursive way.'''
    if type(children) is list and children:
        child = children.pop(0)
        node_idx = write_node_definition(
            out_file,
            child,
            node_idx)
        child_idx = node_idx
        write_transition(out_file, parent_idx, node_idx)
        for grand_child in children:
            node_idx = rekursive_dot_write(
                out_file,
                child_idx,
                grand_child,
                node_idx)
        return node_idx
    if type(children) is str:
        node_idx = write_node_definition(
            out_file,
            children,
            node_idx)
        write_transition(out_file, parent_idx, node_idx)
        return node_idx
    else:
        print 'Empty or odd list while generationg dot file.'
        return node_idx
    return node_idx


def rekursive_dot_write_init(out_file, tree_as_list):
    '''Prepare tree list for rekursive translation
       of tree levels to dot format.'''
    node_idx = -1
    if len(tree_as_list) > 1:
        # iterate list 2-tuple wise to catch
        # parent children combinations
        parent = tree_as_list.pop(0)
        # get dot reference for parent node
        parent_idx = write_node_definition(
            out_file,
            parent,
            node_idx)
        node_idx = parent_idx
        for child in tree_as_list:
            # write children
            node_idx = rekursive_dot_write(
                out_file,
                parent_idx,
                child,
                node_idx)
    # in case tree consists of a single root note
    else:
        print 'Empty or odd list while generationg dot file.'
        sys.exit()


def write_dot_file_helper((idx, name, tree_list), dot_dir):
    '''Write a dot version of the tree to file.'''
    if tree_list:
        # iterate over tree version while enumerating them
        for (tree_idx, tree) in enumerate(tree_list, 1):
            # assemble file name
            filename = '{}{}{}_{}.dot'.format(
                dot_dir, str(idx), '_{}'.format(str(tree_idx)), name)
            # prepare file
            out_file = open(filename, 'w')
            # write graph definition to file
            out_file.write('digraph G {\n')
            # tree string to list
            tree_as_list = grammar.tree_string_to_list(
                tree.replace(',', ''))
            # write dot definition body
            rekursive_dot_write_init(out_file, tree_as_list[0])
            out_file.write('}')
            out_file.close()


def write(items, dot_dir, verbose):
    '''Wrapper function.'''
    if verbose:
        bar = Bar('Generating dot files\t', max=len(items))
    for elem in items:
        write_dot_file_helper(elem, dot_dir)
        if verbose:
            bar.next()
    if verbose:
        bar.finish()
        print 'Writing dot files to {}'.format(dot_dir)
