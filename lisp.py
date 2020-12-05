import math
import operator as op

Symbol = str              # A Scheme Symbol is implemented as a Python str
Number = (int, float)     # A Scheme Number is implemented as a Python int or float
Atom   = (Symbol, Number) # A Scheme Atom is a Symbol or Number
List   = list             # A Scheme List is implemented as a Python list
Exp    = (Atom, List)     # A Scheme expression is an Atom or List
Env    = dict             # A Scheme environment (defined below) 
                            # is a mapping of {variable: value}
def parse(program):
    "Read a Scheme expression from a string."
    return read_from_tokens(tokenize(program))

def tokenize(s):
    "Convert a string into a list of tokens."
    return s.replace('(',' ( ').replace(')',' ) ').replace('\n', ' ').split()

def read_from_tokens(tokens):
    "Read an expression from a sequence of tokens."
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF while reading')
    token = tokens.pop(0)
    if '(' == token:
        L = []
        while tokens[0] != ')':
            L.append(read_from_tokens(tokens))
        tokens.pop(0) # pop off ')'
        return L
    elif ')' == token:
        raise SyntaxError('unexpected )')
    else:
        return atom(token)

def atom(token: str) -> Atom:
    "Numbers become numbers; every other token is a symbol."
    try: return int(token)
    except ValueError:
        try: return float(token)
        except ValueError:
            return Symbol(token)

def standard_env() -> Env:
    "An environment with some Scheme standard procedures."
    env = Env()
    env.update(vars(math)) # sin, cos, sqrt, pi, ...
    env.update({
        '+':op.add, '-':op.sub, '*':op.mul, '/':op.truediv, 
        '>':op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq, 
        'abs':     abs,
        'append':  op.add,  
        'apply':   lambda proc, args: proc(*args),
        'begin':   lambda *x: x[-1],
        'CAR':     lambda x: x[0],
        'CDR':     lambda x: x[1:], 
        'cons':    lambda x,y: [x] + y,
        'eq?':     op.is_, 
        'expt':    pow,
        'equal?':  op.eq, 
        'length':  len, 
        'LIST':    lambda *x: List(x), 
        'list?':   lambda x: isinstance(x, List), 
        'map':     map,
        'max':     max,
        'min':     min,
        'not':     op.not_,
        'null?':   lambda x: x == [], 
        'number?': lambda x: isinstance(x, Number),  
		'PRINT':   print,
        'procedure?': callable,
        'round':   round,
        'symbol?': lambda x: isinstance(x, Symbol),
    })
    return env

class Env(dict):
    "An environment: a dict of {'var':val} pairs, with an outer Env."
    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer
    def find(self, var):
        "Find the innermost Env where var appears."
        return self if (var in self) else self.outer.find(var)
    
class Procedure(object):
    "A user-defined Scheme procedure."
    def __init__(self, parms, body, env):
        self.parms, self.body, self.env = parms, body, env
    def __call__(self, *args): 
        return eval(self.body, Env(self.parms, args, self.env))

global_env = standard_env()

def eval(x, env=global_env):
    "Evaluate an expression in an environment."
    if isinstance(x, Symbol):    # variable reference
        return env.find(x)[x]
    elif not isinstance(x, List):# constant
        return x   
    op, *args = x       
    if op == 'if':             # conditional
        (test, conseq, alt) = args
        exp = (conseq if eval(test, env) else alt)
        return eval(exp, env)
    elif op == 'SETQ':         # definition        
        (symbol, exp) = args
        env[symbol] = eval(exp, env)
        print(symbol)
    elif op == 'set!':           # assignment
        (symbol, exp) = args
        env.find(symbol)[symbol] = eval(exp, env)
    elif op == 'lambda':         # procedure
        (parms, body) = args
        return Procedure(parms, body, env)
    else:                        # procedure call
        proc = eval(op, env)
        vals = []
        flag= False
        for arg in args :
            if arg == '\'':
                flag = True
            elif flag == True:
                vals.append(arg)
                flag = False
            elif flag == False:
                vals.append(eval(arg,env))
        return proc(*vals)

def printList(List : list) :
    print("(", end="")
    for element in List:
        if type(element) == list :
            printList(element)
        else:
            if element == List[len(List)-1]:
                print(element, end ="")
            else :
                print(element, end= " ")
    print(")", end="")

f = open("C:/PL_LISP/code.in", 'r')
inputs = f.readlines()

for line in inputs:
    result = eval(parse(line))
    if type(result) == list:
        print("(",end="")
        for element in result:
            if type(element) == list :
                printList(element)
                if(element == result[len(result)-1]):
                    print(end="")
                else:
                    print(end=" ")
            else:
                if element == result[len(result)-1]:
                    print(element, end="")
                else:
                    print(element, end=" ")
        print(") ",end="\n")

f.close()

