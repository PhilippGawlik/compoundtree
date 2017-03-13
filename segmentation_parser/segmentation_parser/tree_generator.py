# -*- coding: utf-8 -*-
'''Define file encoding.'''


class TreeGeneratorException(Exception):
    pass


def tree_string_to_list(tree):
    '''Parse tree string to list.'''
    parse_input = '({})'.format(tree)
    return nestedExpr().parseString(parse_input).asList()[0]


def parse_final_stem(result):
    ''' Transform parser result:

        [ 'final stem', 'suffix'*]

        to bracket structure:

        ('nbase' 'stem') ... (Optional suffixes)
    '''
    #print 'Final stem parse result: %s' % str(result)
    if len(result) > 1:
        # rename suffix type
        suffix_str = ' '.join(result[1:])
        suffix_str = suffix_str.replace('SUFFIX', 'NSUFFIX')
        return '(nbase {}) {}'.format(result[0], suffix_str)
    return '(nbase {})'.format(result[0])


def split_suffix_structures(result):
    '''Parses might return complex parse strings
       like "(a b) (c d)" that need to be split
       into separate tuple strings like "(a b)"
       and "(c d)".'''
    split_suffix_results = []
    for elem in result:
        while elem.find(') (') > -1:
            idx = elem.find(') (')
            split_suffix_results.append(elem[0:idx+1])
            elem = elem[idx+2:]
        split_suffix_results.append(elem)
    return split_suffix_results


CAT_DICT = {
    'nbase': 'noun',
    'NSUFFIX': 'noun',
    'SUFFIX': 'affix',
    'vbase': 'verb',
    'abase': 'adj',
    'pbase': 'prt',
    'fbase': 'f',
    'kbase': 'k',
    'zbase': 'z',
    'xbase': 'x',
    'locbase': 'loc',
    'namebase': 'name',
    'probase': 'pro',
    'orgbase': 'org',
    'evebase': 'eve',
    'egobase': 'ego',
    'geobase': 'geo',
    'fmbase': 'fm',
    'PARTICLE': 'prt',
    'link': 'link'
}


def get_root_node(lroot, rroot):
    '''Get name for parent node while binary merge of trees.'''
    if rroot in ['link', 'suffix']:
        return lroot
    return rroot


def merge(lhs, rhs, cat_dict=CAT_DICT):
    ''' Merge trees.'''
    (lroot, llhs, lrhs) = lhs
    (rroot, rlhs, rrhs) = rhs
    root = get_root_node(lroot, rroot)
    return (root, lhs, rrhs)


def build_binary_subtrees(term_list, cat_dict=CAT_DICT):
    ''''''
    binary_tree_list = []
    last_term = ''
    for term in term_list:
        if term == '#':
            if last_term:
                binary_tree_list.append(last_term)
                last_term = ''
        else:
            if last_term:
                last_term = merge(last_term, term)
            else:
                last_term = term
    binary_tree_list.append(last_term)
    return binary_tree_list


def treetostring(tup):
    ''''''
    if type(tup) == str:
        return tup
    (root, lhs, rhs) = tup
    if type(lhs) == tuple:
        lhs = treetostring(lhs)
    if type(rhs) == tuple:
        rhs = treetostring(rhs)
    if lhs == '':
        return '({} {})'.format(root, rhs)
    return '({} {} {})'.format(root, lhs, rhs)


def balanced_append((i, j, tree)):
    '''Tuple two subtrees of the list in "tree"
       to generate a binary branching relation.

         rooti      rootj
           |          |
       childreni    childrenj

       The new root node is a comp node
       that subordinates the two subtrees.

               comp
               /  \
              /    \
           rooti  rootj
             |      |
       childreni  childrenj

       '''
    bal_tree = list(tree)
    bal_tree[i] = ('comp', bal_tree[i], bal_tree[j])
    bal_tree.pop(j)
    return bal_tree


def left_append((i, j, tree)):
    '''Tuple two subtrees of the list in "tree"
       to generate a binary branching relation.

         rooti      rootj
           |          |
       childreni    childrenj

       The new root node is a comp node
       that replaces the root node of
       the left hand subtree indexed with
       index i. The result looks like:

               comp
               /  \
              /    \
        childreni rootj
                    |
                  childrenj

       '''
    subtreei = ""
    subtreej = ""
    left_tree = list(tree)
    # append to the left
    (_, lhsi, rhsi) = left_tree[i]
    # condition the structure of the
    # right hand side subtree on the
    # head of the left hand subtree

    # if left hand subree has root 'comp'
    # the right hand subtree is append
    # with no root node'
    if lhsi:
        subtreei = compose_branching(lhsi, rhsi)
        (_, lhsj, rhsj) = left_tree[j]
        if lhsj:
            subtreej = compose_branching(lhsj, rhsj)
        else:
            subtreej = rhsj
    else:
        subtreei = str(rhsi)
        subtreej = treetostring(tree[j])
    left_tree[i] = ('comp', subtreei, subtreej)
    left_tree.pop(j)
    return left_tree


def compose_branching(lhs, rhs):
    ''''''
    lhs = treetostring(lhs)
    rhs = treetostring(rhs)
    if lhs:
        subtree = '(comp {} {})'.format(str(lhs), str(rhs))
    else:
        subtree = str(rhs)
    return subtree


def right_append((i, j, tree)):
    '''Tuple two subtrees of the list in "tree"
       to generate a binary branching relation.

         rooti      rootj
           |          |
       childreni    childrenj

       The new root node is a comp node
       that replaces the root node of
       the right hand subtree indexed with
       index j. The result looks like:

               comp
               /  \
              /    \
           rooti  childrenj
            |
        childreni

       '''
    subtreei = ""
    subtreej = ""
    right_tree = list(tree)
    # append to the right
    (_, lhsj, rhsj) = right_tree[j]
    # condition the structure of the
    # left hand side subtree on the
    # head of the right hand subtree

    # if right hand subree has root 'comp'
    # the left hand subtree is append
    # with no root node'
    if lhsj:
        (_, lhsi, rhsi) = right_tree[i]
        if rhsi:
            subtreei = compose_branching(lhsi, rhsi)
        else:
            subtreei = rhsi
        subtreej = compose_branching(lhsj, rhsj)
    else:
        subtreei = treetostring(tree[i])
        subtreej = str(rhsj)
    right_tree[i] = ('comp', tree[i], tree[j])
    right_tree.pop(j)
    return right_tree


def build_trees(in_list):
    ''' Build binary trees from subtree list.'''
    tree_list = []
    # initial tree
    buff_list = [in_list]
    while buff_list:
        tree = buff_list.pop(0)
        if len(tree) > 2:
            copy_list = []
            # copy list n times
            # to generate a tree with
            # every possible combination
            # of a subtree tuple
            # n = len(list)-1
            for it in range(0, len(tree)-1):
                copy_list.append(list(tree))
            # zip list with a copy of the tree
            # and the indices ot the subtrees
            # to be tupled
            ind_list = zip(
                range(0, len(tree)-1), range(1, len(tree)), copy_list)
            # build the tree with the new tuples
            for ind_elem in ind_list:
                buff_list.append(balanced_append(ind_elem))
        elif len(tree) == 2:
            buff_list.append(balanced_append((0, 1, tree)))
        elif len(tree) == 1:
            tree_list.append(treetostring(tree[0]))
        else:
            print 'Error: tree contains zero elements.'
    return tree_list


def make_root_tree(term_list, cat_dict=CAT_DICT):
    ''''''
    rooted_term_list = []
    for term in term_list:
        if term == '#':
            rooted_term_list.append(term)
        else:
            (base, word) = term[1:-1].split()
            # simplification of link root node
            if base[0:4] == 'link':
                root = 'link'
            else:
                root = cat_dict.get(base, base)
            rooted_term_list.append((root, '', (base, '', word)))
    return rooted_term_list


def generate(result):
    ''' Transform parser result:

        [ 'parse tree']

        (parent, lhs, rhs)

    '''
    term_list = split_suffix_structures(result)
    # print 'Compound parse result: %s' % str(term_list)
    term_list = make_root_tree(term_list)
    # print 'Prepared base trees: %s' % str(term_list)
    term_list = build_binary_subtrees(term_list)
    # print 'Binary subtree list: {}'.format(term_list)
    tree_list = build_trees(term_list)
    # print 'Compound tree list: {}'.format(term_list)
    # remove duplicate trees
    tree_list = list(set(tree_list))
    # for tree in tree_list:
        # print '\tTree: {}'.format(tree)
    return tree_list
