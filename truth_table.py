#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Generates truth tables with pandas
from data import Constant
from parser import parse
import pandas as pd

def df2md(df):
    output = []

    lengths = [max(len(s), 3) for s in df.columns]
    form    = ["%%%ds" % l for l in lengths]

    output.append(' | '.join(f % s for f,s in zip(form, df.columns.values)))
    output.append(' | '.join("-" * l for l in lengths))

    for index, row in df.iterrows():
        output.append(' | '.join(f % r for f,r in zip(form, row)))
    return '\n'.join(output)

def truth_table(expr):
    variables = sorted(expr.variables())

    # We want the easiest expressions first, also True/False are not interesting
    sub_expr  = [(s.depth(),str(s), s) for s in expr.expressions() if not isinstance(s, Constant)]
    sub_expr.sort()
    sub_labl  = [lab for d,lab,s in sub_expr]
    sub_expr  = [s for d,lab, s in sub_expr]

    # var -> True | False
    bool_map = {}
    # [[output,...,output], [output,...,output]]
    res = [[] for _ in sub_expr]

    assert len(sub_expr) == len(sub_labl)

    for perm in range(2 ** len(variables)):
        # create bool map from integer
        for o, var in enumerate(variables):
            bool_map[var] = (perm >> o) & 1 == 1

        for i, s in enumerate(sub_expr):
            res[i].append(Constant._out_symbols[s.calc(bool_map)])

    return pd.DataFrame(zip(*res), columns=sub_labl)

if __name__ == '__main__':
    from argparse import ArgumentParser
    PARSER = ArgumentParser(description='truth table maker')
    PARSER.add_argument("-o", "--output", choices=["md", "latex", "html"], default="md")
    PARSER.add_argument("statement", type=str)
    ARGS = PARSER.parse_args()

    expr  = parse(ARGS.statement)
    #expr  = parse(r'(A -> A) implies not (B * ((((~A))))) && (A -> A)')
    table = truth_table(expr)

    if ARGS.output == 'md':
        print df2md(table)
    elif ARGS.output == 'latex':
        print table.to_latex(index=False)
    else:
        print table.to_html(index=False)
