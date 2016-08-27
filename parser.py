#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Parser
from pyparsing import *
from data import create_var_const, create_expression, infix_operators, prefix_operators

# def caseless_keywords(keywords):
#     prior = CaselessKeyword(keywords[0])
#     for i in range(1, len(keywords)):
#         prior += CaselessKeyword(keywords[i])
#     return prior

__bnf = None
def _bnf():
    global __bnf
    if __bnf:
        return __bnf
    # variable    := Word of letters
    # atom        := 'True' | 'False' | variable | '(' expression ')'
    # prefix_expr := [ prefix ]* atom
    # expression  := prefix_expr [ infix_operator prefix_expr ]
    expression  = Forward()
    infix_op    = oneOf(infix_operators,  caseless=True)
    prefix_op   = oneOf(prefix_operators, caseless=True)
    varconst    = Word(alphas + '_').setParseAction(lambda t:create_var_const(t[0]))
    nest        = Suppress('(') + expression + Suppress(')')
    atom        = varconst | nest
    prefix_expr = (ZeroOrMore(prefix_op) + atom).setParseAction(parse_prefix_op)
    expression << (prefix_expr + ZeroOrMore(infix_op + prefix_expr))
    expression.setParseAction(parse_infix_op)
    __bnf = expression
    return __bnf

def parse_prefix_op(strg, loc, toks):
    for i, t in enumerate(toks[::-1]):
        res = t if i == 0 else create_expression(t, res)
    return res

def parse_infix_op(strg, loc, toks):
    left = toks[0]

    for op, right in zip(toks[1::2], toks[2::2]):
        left = create_expression(op, left, right)
    return left

    # gen = iter(toks)
    # left  = next(gen)
    # for op in gen:
    #     right = next(gen)
    #     left = operator_class[op](left, right)
    # return left

def parse(string):
    return _bnf().parseString(string)[0]

if __name__ == '__main__':
    test_cases = """
    ((a or c) or d)
    b * (((a))) + d * shit * crazy
    throw_money_in_machine implies candy_rolls_out
    (a implies a) implies (a or ¬ b ^ c)
    """.strip().split('\n')

    for expr_in in test_cases:
        print "input :%s" % expr_in
        expr_out = parse(expr_in)
        print "output:%s" % str(expr_out)
