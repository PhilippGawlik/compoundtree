# -*- coding: utf-8 -*-
'''Define file encoding.'''

# --------------------------------------------
# ---------- PYPARSING GRAMMAR ---------------
# --------------------------------------------
import pyparsing as pp
from pyparsing import nestedExpr


class BadParseException(Exception):
    pass


# ---------- Parse Action Definitions --------


def list_to_string(result):
    '''Transform a list of string to a string.'''
    return ', '.join(result)


def normalise_parser_output(result_list):
    '''Convert parser output of type
    pyparsing.ParseResult to type list.'''
    norm_list = []
    for result in result_list:
        print 'result in normalisation: {}'.format(result)
        norm_list.append(result.asList())
    return norm_list


def tree_string_to_list(tree):
    '''Parse tree string to list.'''
    parse_input = '({})'.format(tree)
    return nestedExpr().parseString(parse_input).asList()[0]


def oops(s, loc, expr, err):
    '''Action to take if parser fails.

       s = input string
       loc = location in input where parser fails
       expr = name of failing parser
       err = the exception instance that parser raised
    '''
    print ("s={0!r} loc={1!r} expr={2!r}\nerr={3!r}".format(
        s, loc, expr, err))


def parse_final_stem(result):
    ''' Transform parser result:

        [ 'final stem', 'suffix'*]

        to bracket structure:

        ('nbase' 'stem') ... (Optional suffixes)
    '''
    if len(result) > 1:
        # rename suffix type
        suffix_str = ' '.join(result[1:])
        suffix_str = suffix_str.replace('SUFFIX', 'NSUFFIX')
        return '(nbase {}) {}'.format(result[0], suffix_str)
    return '(nbase {})'.format(result[0])


def parse_final_type_stem(result):
    ''' Transform parser result:

        [ 'final stem', '<', 'type', '>', 'suffix'*]

        to bracket structure:

        ('nbase' 'stem') ... (Optional suffixes)
    '''
    stem = result[0]
    stype = result[2]
    if len(result) > 4:
        # rename suffix type
        suffix_str = ' '.join(result[4:])
        suffix_str = suffix_str.replace(
            '(SUFFIX',
            '(NSUFFIX')
        return '({0}base {1}) {2}'.format(
            stype.lower(),
            stem,
            suffix_str)
    return '(nbase {1})'.format(
            stype.lower(),
            stem)


def parse_stem_suffix(result):
    ''' Transform parser result:

        ['stem', suffix*]

        to tree structure:

        ('stem' 'typeSUFFIX') ... (Optional suffixes)
    '''
    stem = result[0]
    if len(result) > 1:
        # rename suffix type
        suffix_str = ' '.join(result[1:])
        return '(nbase {0}) {1}'.format(
            stem,
            suffix_str)
    return '(nbase {0})'.format(
            stem)


def parse_stem_type_suffix(result):
    ''' Transform parser result:

        ['stem', '<', 'stype', '>', suffix*]

        to tree structure:

        ('typebase' 'stem') ... (Optional suffixes)
    '''
    stem = result[0]
    stype = result[2]
    if len(result) > 4:
        # rename suffix type
        suffix_str = ' '.join(result[4:])
        return '({0}base {1}) {2}'.format(
            stype.lower(),
            stem,
            suffix_str)
    return '({0}base {1})'.format(
            stype.lower(),
            stem)


def parse_single_stem(result):
    ''' Transform parser result:

        [ 'single stem']

        to tree structure:

             nbase
               |
               |
             NSTEM
               |
               |
          single_stem

    '''
    return 'nbase(NSTEM({}))'.format(result[0])


def parse_compound(result):
    ''' Transform parser result:

        [ 'parse tree']

        (parent, lhs, rhs)

    '''
    return result


def parse_hash_term(result):
    ''' Transform parser result:
        [ '#']

    '''
    return 'COMPOS_MARK(#)'


def parse_stem_type(result):
    ''' Transform parser result:

        [['stem'], '<', 'stype', '>']

        to tree structure:

        ('typebase' 'stem')
    '''
    stype = result[2]
    stem = result[0]
    return '({0}base {1})'.format(
            stype.lower(),
            stem)


def parse_particle(result):
    ''' Transform parser result:

        ['particle_stem', '<', 'prt', '>']

        to tree structure:

        ('particle' 'stem')

    '''
    particle_stem = result[0]
    return '(PARTICLE {})'.format(
            particle_stem)


def parse_prefix(result):
    ''' Transform parser result:

        ['stem', '<', 'p', '>']

        to tree structure:

        ('stem' 'stem')

    '''
    prefix_stem = result[0]
    return '({0} {0})'.format(
            prefix_stem)


def parse_verb_prefix_mark(result):
    ''' Transform parser result:

        [ '=']

        to tree structure:

        '='

    '''
    return '='


def parse_link(result):
    ''' Transform parser result:

        ['link_stem']

        to tree structure:

        ('link_stem', 'stem')

    '''
    link_stem = (result[0]).replace('\\', '')
    return '(link_{0} {0})'.format(
            link_stem)


def parse_link_stem_type(result):
    ''' Transform parser result:

        ['link_stem', '<', 'link_type', '>']

        to tree structure:

        ('link_stem', 'stem')

    '''
    return result[0]


def parse_suffix_mark(result):
    ''' Transform parser result:

        ['~']

        to tree structure:

            SUFFIX_MARK
               |
               |
               ~
    '''
    return ''


def parse_suffix_type(result):
    ''' Transform parser result:

        ['suffix_mark', 'suffix_stem', '<', 'suffix_type', '>']

        to tree structure:

        ('SUFFIX' 'stem')

    '''
    suffix_stem = result[1]
    suffix_type = result[3]
    if suffix_type == 'Part':
        return '(PARTICLE {0})'.format(
                suffix_stem)
    elif suffix_type == 'n':
        return '(NSUFFIX {0})'.format(
                suffix_stem)
    else:
        return '(SUFFIX {0})'.format(
                suffix_stem)


def parse_part_type(result):
    ''' Transform parser result:

        ['suffix_mark', 'suffix_stem', '<', 'part_type', '>']

        to tree structure:

        ('PARTICLE' 'stem')

    '''
    suffix_stem = result[1]
    return '(PARTICLE {0})'.format(
            suffix_stem)


def parse_suffix_term(result):
    ''' Transform parser result:

        ['suffix_stem']

        to tree structure:

        ('SUFFIX' 'stem')
    '''
    suffix_stem = result[0]
    return '(SUFFIX {0})'.format(suffix_stem)


# ---------- Parsers ----------------------------------

# Constantes

STEM_TYPES = ['NAME', 'N', 'GEO', 'EGO', 'A', 'ORG', 'X', 'LOC', 'PRO', 'EVE',
              'Z', 'z', 'FM', 'K', 'k', 'ADV', 'n', 'Part', 'f', 'V']

# Terminal Parsers

stem_term = pp.Word(pp.alphas + '=' + '+' + '-' + '|' + 'ÄäÜüÖößéèâê')
stem_types = pp.Or(STEM_TYPES)
verb_mark = pp.Word('V')
verb_prefix_type = pp.Word('prt')
prefix_type = pp.Word('p')
open_brack_term = pp.Word('<')
close_brack_term = pp.Word('>')
prior_mark = pp.Word('@')
hash_term = pp.Word('#')
verb_prefix_mark = pp.Word('=').setParseAction(parse_verb_prefix_mark)
link_type = pp.Word('l')
link_term = pp.Word(pp.alphas + 'ÄäÜüÖöß' + '\\').ignore('\\')
suffix_mark = pp.Word('~')
suffix_types = pp.Word('a' + 'N' + 'V' + 'n' + 'Z' + 'z' + 'v' + 'I' + 'A' +
                       'k' + 'X' + 'Part')
suffix_term = pp.Word(pp.alphas + 'ÄäÜüÖöß')
suffix_term_blank = pp.Word(pp.alphas + 'ÄäÜüÖöß')
formativ_type = pp.Word('f')

# Nonterminal Parsers

stem_type = (
    stem_term +
    open_brack_term +
    stem_types +
    close_brack_term
    ).setParseAction(parse_stem_type)

verb_type = (
    stem_term +
    open_brack_term +
    verb_mark +
    close_brack_term
    ).setParseAction(parse_stem_type)

particle = (
    stem_term +
    open_brack_term +
    verb_prefix_type +
    close_brack_term
    ).setParseAction(parse_particle)

prefix = (
    stem_term +
    open_brack_term +
    prefix_type +
    close_brack_term
    ).setParseAction(parse_prefix)

link = (
    link_term
    ).setParseAction(parse_link)

link_stem_type = (
    link_term +
    open_brack_term +
    link_type +
    close_brack_term
    ).setParseAction(parse_link_stem_type)

suffix_type = (
    suffix_mark +
    suffix_term_blank +
    open_brack_term +
    suffix_types +
    close_brack_term
    ).setParseAction(parse_suffix_type)

suffix = (
    pp.Suppress(suffix_mark) +
    suffix_term.setParseAction(parse_suffix_term)
    )

stem_suffix = (
    stem_term +
    pp.ZeroOrMore(
        suffix_type ^
        suffix
        )
    ).setParseAction(parse_stem_suffix)

stem_type_suffix = (
    stem_term +
    open_brack_term +
    stem_types +
    close_brack_term +
    pp.ZeroOrMore(
        suffix_type ^
        suffix ^
        link_stem_type ^
        link
        )
    ).setParseAction(parse_stem_type_suffix)

verb_suffix_type = (
    stem_term +
    suffix +
    open_brack_term +
    verb_type +
    close_brack_term
    ).setParseAction(parse_stem_suffix)

final_stem = (
    stem_term +
    pp.ZeroOrMore(
        suffix_type ^
        suffix ^
        link_stem_type ^
        link
        ) +
    pp.StringEnd()
    ).setParseAction(parse_final_stem)

final_type_stem = (
    stem_term +
    open_brack_term +
    stem_types +
    close_brack_term +
    pp.ZeroOrMore(
        suffix_type ^
        suffix ^
        link_stem_type ^
        link
        ) +
    pp.StringEnd()
    ).setParseAction(parse_final_type_stem)

compound = (
    pp.OneOrMore(
        # parsing head stem
        final_stem ^
        final_type_stem ^
        # parsing stem
        stem_type_suffix ^
        stem_suffix ^
        pp.Suppress(prior_mark) ^
        hash_term ^
        prefix ^
        particle ^
        verb_prefix_mark
        )
    ).setParseAction(parse_compound)
