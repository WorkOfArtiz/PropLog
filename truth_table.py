#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Generates truth tables with pandas
from data import Constant
from parser import parse
import pandas as pd

def df2md(df):
    output = []

    output.append(' | '.join(df.columns.values))
    output.append(' | '.join("-"*len(l) for l in df.columns.values))

    form = ["%%%ds" % len(l) for l in df.columns.values]

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
    expr  = parse(r'(A -> A) implies not (B * ((((~A))))) && (A -> A)')
    table = truth_table(expr)
    print table.to_html(index=False)
    #print table.to_latex(index=False) #df2md(table)
