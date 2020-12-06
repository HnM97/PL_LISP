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
    return s.upper().replace('(',' ( ').replace(')',' ) ').replace('\'', ' \' ').split()

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
        'ABS':     abs,
        'APPEND':  lambda x, y, z : [x]+y+z,  
        'apply':   lambda proc, args: proc(*args),
        'begin':   lambda *x: x[-1],
        'CONS':    lambda x,y: [x] + y,
        'EQ?':     op.is_, 
        'EXPT':    pow,
        'EQUAL?':  op.eq, 
        'LENGTH':  len, 
        'LIST':    lambda *x: List(x),
        'REVERSE': lambda *x: List(x), 
        'LISTP?':   lambda x: isinstance(x, List), 
        'map':     map,
        'max':     max,
        'min':     min,
        'not':     op.not_,
        'NULL?':   lambda x: x == [], 
        'NUMBERP?': lambda x: isinstance(x, Number),  
		'PRINT':   print,
        'procedure?': callable,
        'round':   round,
        'ATOM': lambda x: isinstance(x, Symbol),
        'STRINGP' : lambda x : isinstance(x,Symbol),
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
        if env.find(x)[x] :
            return env.find(x)[x]
        elif x[0]=='\'':
            x = x.split(sep='\'')[1]
            return x
        else :
            return x

    elif not isinstance(x, List):# constant
        return x   
    op, *args = x       
    if op == 'IF':             # conditional
        if len(args)==3:
            (test, conseq, alt) = args
            exp = (conseq if eval(test, env) else alt)
            return eval(exp, env)
        else:
            (test, conseq) = args
            if eval(test,env):
               exp = conseq
            else:
                print("NIL")
            return eval(exp,env) 
    elif op == 'SETQ':         # definition
        if args[1]=='\'':
            symbol = args[0]
            
            if type(args[2]) == int:
                exp = args[2:]
            else :
                exp = args[2]
                print(exp)
            env[symbol] = exp
        else:
            (symbol, exp) = args
            env[symbol] = eval(exp, env)
        print(symbol)
    elif op == 'set!':           # assignment
        (symbol, exp) = args
        env.find(symbol)[symbol] = eval(exp, env)
    elif op == 'lambda':         # procedure
        (parms, body) = args
        return Procedure(parms, body, env)
    elif type(op) == int:
        return x  

    elif op == 'NTH':           
        index=args[0]
        nthlist=args[2]
        if(not isinstance(nthlist,List)):
            print("ERROR")
        else:
            if(index>len(nthlist)):
                print("NIL")
            else:
                return nthlist[index]

    elif op == 'MEMBER':
        if args[0] == '\'':
            exp = args[1]
            symbol = args[2]
        else:
            (exp,symbol) = args
        if exp in env[symbol]:
            index = env[symbol].index(exp)
            print(env[symbol][index:])
        else:
            print("NIL")
            
    elif op == 'REMOVE':
        if args[0] == '\'':
            exp = args[1]
            symbol = args[2]
        else:
            (exp,symbol) = args
        while exp in env[symbol]:
            index = env[symbol].index(exp)
            env[symbol].pop(index)
        printList(env[symbol])

    elif op == "SUBST":
        while '\'' in args:
            index = args.index('\'')
            args.pop(index)
        (first, second, third) = args
        if second in third:
            index = third.index(second)
            third.insert(index, first)
            third.pop(index+1)
            printList(third)
        else:
            print("NILL")

    elif op == "ASSOC":
        flag=False
        while '\'' in args:
            index = args.index('\'')
            args.pop(index)
        (target, dictionary) = args
        for listelem in dictionary:
            if listelem[0] == target:
                printList(listelem)   
                flag = True
        if flag == False:
            print("NILL")
          
    elif op == 'APPEND':
        while '\'' in args:
            index = args.index('\'')
            args.pop(index)
        sumList= []
        for elem in args:
            sumList += elem
        printList(sumList)
    
    elif op == 'CAR':
        exp = args[1]
        if type(exp[0])== list:
            printList(exp[0])
        else: 
            print(exp[0])
    
    elif op == 'CDR':
        if args[0]!='\'':
            symbol = args[0]
            env[symbol] = env[symbol][1:]
        else:
            exp = args[1]
            printList(exp[1:])
        
    else:                        # procedure call
        proc = eval(op, env)
        vals = []
        flag= False
        symbol = 0

        if isinstance(args[0],Symbol) :
            symbol = args[0]
            args.pop(0)

        for arg in args :
            if arg == '\'':
                flag = True
            elif flag == True:
                vals.append(arg)
                flag = False
            elif flag == False:
                vals.append(eval(arg,env))

        if op== 'REVERSE':
            vals.reverse()

        if isinstance(args[0],Symbol) :
            env[symbol] = proc(*vals)     
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
    elif (type(result)==int) or (type(result)==float):
        print(result)

    f.close()

