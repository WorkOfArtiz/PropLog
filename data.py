#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Data components for logic expressions
# Should be easily extendible and adaptable
#
# These data components are supposed to be immutable.
class LogicExpression:
    _symbols = []           # A data container for all operators for expr
    _out_symbol = 'nothing' # The symbol used to output
    class_name  = 'None'    # Text representing class
    # boolean map: var -> boolean, mapping every variable
    # returns the value of the expression
    def calc(self, boolean_map):
        raise NotImplementedError()

    # returns set of sub expressions
    def expressions(self):
        raise NotImplementedError()

    # returns the amount of levels of expressions
    def depth(self):
        raise NotImplementedError()

    # returns generator that loops through sub expressions
    def children(self):
        raise NotImplementedError()

class And(LogicExpression):
    _symbols = ('and', '&&', '&', '^', '/\\', '∧', '*')
    _out_symbol = '^'
    class_name = 'and'

    def __init__(self, l, r):
        self._left, self._right = l, r
    def __str__(self):
        return "(%s %s %s)" % (self._left, And._out_symbol, self._right)
    def __repr__(self):
        return "And(%s,%s)" % (self._left.__repr__(), self._right.__repr__())
    def calc(self, boolean_map):
        return self._left.calc(boolean_map) & self._right.calc(boolean_map)
    def expressions(self):
        e = self._left.expressions()
        e.add(self)
        e.update(self._right.expressions())
        return e
    def depth(self):
        return max(self._left.depth(), self._right.depth()) + 1
    def variables(self):
        return self._left.variables().union(self._right.variables())
    def children(self):
        yield self._left
        yield self._right
class Or(LogicExpression):
    _symbols = ('or', '||', '|', 'v', '\\/', '∨', '+')
    _out_symbol = 'v'
    class_name = 'or'
    def __init__(self, l, r):
        self._left, self._right = l, r
    def __str__(self):
        return "(%s %s %s)" % (self._left, Or._out_symbol, self._right)
    def __repr__(self):
        return "Or(%s, %s)" % (self._left.__repr__(), self._right.__repr__())
    def calc(self, boolean_map):
        return self._left.calc(boolean_map) | self._right.calc(boolean_map)
    def expressions(self):
        e = self._left.expressions()
        e.add(self)
        e.update(self._right.expressions())
        return e
    def depth(self):
        return max(self._left.depth(), self._right.depth()) + 1
    def variables(self):
        return self._left.variables().union(self._right.variables())
    def children(self):
        yield self._left
        yield self._right
class Implies(LogicExpression):
    _symbols = ('implies', '->', '=>', '→')
    _out_symbol = '->'
    class_name  = 'implies'
    def __init__(self,l,r):
        self._left,self._right=l,r
    def __str__(self):
        return "(%s %s %s)" % (self._left,Implies._out_symbol, self._right)
    def __repr__(self):
        return "Implies(%s, %s)" % (self._left.__repr__(), self._right.__repr__())
    def calc(self, boolean_map):
        l = self._left.calc(boolean_map)
        if not l:
            return True
        return l & self._right.calc(boolean_map)
    def expressions(self):
        e = self._left.expressions()
        e.add(self)
        e.update(self._right.expressions())
        return e
    def depth(self):
        return max(self._left.depth(), self._right.depth()) + 1
    def variables(self):
        return self._left.variables().union(self._right.variables())
    def children(self):
        yield self._left
        yield self._right
class Not(LogicExpression):
    _symbols = ('not', '~', '¬', '!')
    _out_symbol = '~'
    class_name  = 'not'

    def __init__(self, e):
        self._expr = e
    def __repr__(self):
        return "~%s" % self._expr.__repr__()
    def __str__(self):
        if isinstance(self._expr, (Var, Constant)):
            return "~%s" % str(self._expr)
        return "~(%s)" % str(self._expr)
        #return "~({expr:s})".format(expr=s.expr)
    def calc(self, boolean_map):
        return not self._expr.calc(boolean_map)
    def expressions(self):
        expr = self._expr.expressions()
        expr.add(self)
        return expr
    def depth(self):
        return self._expr.depth() + 1
    def variables(self):
        return self._expr.variables()
    def children(self):
        yield self._expr
class Var(LogicExpression):
    class_name = 'var'
    def __init__(self, n):
        self.name = n
    def __str__(self):
        return "%s" % self.name
    def __repr__(self):
        return "{%s}" % self.name
    def calc(self, boolean_map):
        v = boolean_map.get(self.name)
        if v == None:
            raise Exception("Error: no value was given for var %s" % self.name)
        return v
    def expressions(self):
        return {self}
    def depth(self):
        return 0
    def variables(self):
        return {self.name}
    def children(self):
        return
        yield
class Constant(LogicExpression):
    _true_symbols  = ('true',  '1')
    _false_symbols = ('false', '0')
    _symbols       = ('true', '1', 'false', '0')
    _out_symbols   = ('0','1')
    class_name     = 'const'

    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return "{True}" if self.value else "{False}"
    def __str__(self):
        return Constant._out_symbols[self.value]
    def calc(self, boolean_map):
        v = boolean_map.get(self.name)
        if v == None:
            raise Exception("Error: no value was given for var %s" % self.name)
        return v
    def expressions(self):
        return {self}
    def depth(self):
        return 0
    def variables(self):
        return set()
    def children(self):
        return
        yield

# The infix classes, prefix classes etc.
infix_classes  = [And, Or, Implies]
prefix_classes = [Not]

# These are some meta data structures, to quickly lookup:
# - what class belongs to what symbol
# - what operators we have
# - what instances already exist
operator_class   = {} # maps a symbol to its class '&' -> class And
infix_operators  = [] # a list of all symbols used for infix operators e.g. '&'
prefix_operators = [] # a list of all symbols used for prefix operators e.g. '~'
instances        = {} # maps a tuple (class, args) to instance, since no duplicates are allowed

# initialise the meta structures
def init_meta_structures():
    for c in infix_classes:
        operator_class.update((s,c) for s in c._symbols)
        infix_operators.extend(c._symbols)
    for c in prefix_classes:
        operator_class.update((s,c) for s in c._symbols)
        prefix_operators.extend(c._symbols)
init_meta_structures()

# Creates an expression from tokens, or if operator is 'var', 'const', 'varconst'
def create_expression(operator, *kwargs):
    if operator in ('var', 'const', 'varconst'):
        return create_var_const(*kwargs)

    constructor = operator_class[operator]
    expr = instances.get((constructor, kwargs))
    if expr == None:
        expr = instances[(constructor, kwargs)] = constructor(*kwargs)
    return expr

# Creates vars and constants (attempt to avoid complicated BNF)
def create_var_const(name):
    if name.lower() in Constant._symbols:
        constructor = Constant
        args = (name.lower() in Constant._true_symbols)
    else:
        constructor = Var
        args        = name

    expr = instances.get((constructor, args))
    if expr == None:
        expr = instances[(constructor, args)] = constructor(name)
    return expr

if __name__ == '__main__':
    # Testing

    # Can vars and constants be properly made
    # for i in ('Abc', 'Note', 'a', 't', 'True', 'False'):
    #     var_const = create_var_const(i)
    #     expr      = create_expression('varconst', i)
    #
    #     print 'input: %s' % i
    #     print repr(var_const)
    #     print repr(expr)
    #     print var_const == expr
    #     print '-'*20

    a = create_var_const('a')
    b = create_var_const('b')
    t = create_var_const('t')
    at = create_expression('&', a, t)

    create_expression('->', a, b)
    create_expression('->', a, b)
    print instances

    # for i in infix_operators:
    #     print 'input (a & t) %s b' % i
    #     expr = create_expression(i, at, b)
    #     expr2 = create_expression(i, at, b)
    #     print expr
    #     print expr == expr2
