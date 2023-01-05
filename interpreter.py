import traceback
import math
Symbol = str
Atom = int | float | str | bool | None


class Env(dict):
    "An environment: a dict of {'var':val} pairs, with an outer Env."

    def __init__(self, params=(), args=(), outer=None):
        self.update(zip(params, args))
        self.outer = outer

    def find(self, var):
        "Find the innermost Env where var appears."
        if var in self:
            return self
        else: 
            if self.outer is not None:
                return self.outer.find(var)
            else: raise Exception(f"Unknown {var}")
            


def add_globals(env: Env) -> Env:
    "Add some built-in procedures and variables to the environment."
    env.update(vars(math))
    env.update(
        {'+': lambda x, y: x + y,
         '-': lambda x, y: x - y,
         '*': lambda x, y: x * y,
         '/': lambda x, y: x / y,
         '>': lambda x, y: x > y,
         '<': lambda x, y: x < y,
         '>=': lambda x, y: x >= y,
         '<=': lambda x, y: x <= y,
         '==': lambda x, y: x == y,
         '^': lambda x, y: x ^ y,
         '!': lambda x: not x,
         '%': lambda x, y: x % y
         })
    env.update({'True': True, 'False': False})
    return env


global_env = add_globals(Env())


def eval(x: list[str], env: Env = global_env) -> Atom | list[any] | Symbol:
    "Evaluate an expression in an environment."
    if isinstance(x, Symbol):              # variable reference
        if x.startswith('\"'):
            return str(x).replace('\"', '')
        return env.find(x)[x]
    elif not isinstance(x, list):          # constant literal
        return x
    elif x[0] == 'quote' or x[0] == 'q':  # (quote exp), or (q exp)
        (_, exp) = x
        return exp
    elif x[0] == 'atom?':           # (atom? exp)
        (_, exp) = x
        return not isinstance(eval(exp, env), list)
    elif x[0] == 'eq?':             # (eq? exp1 exp2)
        (_, exp1, exp2) = x
        v1, v2 = eval(exp1, env), eval(exp2, env)
        return (not isinstance(v1, list)) and (v1 == v2)
    elif x[0] == 'car':             # (car exp)
        (_, exp) = x
        return eval(exp, env)[0]
    elif x[0] == 'cdr':             # (cdr exp)
        (_, exp) = x
        return eval(exp, env)[1:]
    elif x[0] == 'cons':            # (cons exp1 exp2)
        (_, exp1, exp2) = x
        return [eval(exp1, env)]+eval(exp2, env)
    elif x[0] == 'cond':            # (cond (p1 e1) ... (pn en))
        for (p, e) in x[1:]:
            if eval(p, env):
                return eval(e, env)
    elif x[0] == 'null?':           # (null? exp)
        (_, exp) = x
        return eval(exp, env) == []
    elif x[0] == 'if':              # (if test conseq alt)
        (_, test, conseq, alt) = x
        return eval((conseq if eval(test, env) else alt), env)
    elif x[0] == 'set!':            # (set! var exp)
        (_, var, exp) = x
        env.find(var)[var] = eval(exp, env)
    elif x[0] == 'define':          # (define var exp)
        (_, var, exp) = x
        env[var] = eval(exp, env)
    elif x[0] == 'lambda':          # (lambda (var*) exp)
        (_, vars, exp) = x
        return lambda *args: eval(exp, Env(vars, args, env))
    elif x[0] == 'begin':           # (begin exp*)
        for exp in x[1:]:
            val = eval(exp, env)
        return val
    elif x[0] == 'env':
        return '( ' + (' '.join(env.keys())) + ' )'
    else:                           # (proc exp*)
        exprs = [eval(exp, env) for exp in x]
        proc = exprs.pop(0)
        return proc(*exprs)


def abstract_syntax_tree(tokens: list[str]) -> tuple[bool, list[list[any] | Atom]]:
    "Read an expression from a sequence of tokens."
    if not len(tokens) > 0:
        return True, None

    token = tokens.pop(0)
    if token == '(':
        nested_expr = []
        while tokens[0] != ')':
            ok, tree = abstract_syntax_tree(tokens)
            if not ok:
                return False, None
            nested_expr.append(tree)
        tokens.pop(0)
        return True, nested_expr
    elif token == ')':
        print('unexpected )')
        return False, None
    else:
        return True, token


def tokenize(line: str) -> list[str]:
    line = line.replace('(', ' ( ')
    line = line.replace(')', ' ) ')

    tokens = []
    i = 0
    while True:
        try:
            c = ord(line[i])
            if c == ord(' '):
                i += 1
                continue
            elif chr(c) in '()+-=/*&!<>':
                operation = chr(c)
                try:
                    if operation in '<>=' and line[i+1] == '=':
                        operation += '='
                except IndexError:
                    pass
                tokens.append(operation)
            elif c in range(ord('0'), ord('9')):
                number = ''
                while c in range(ord('0'), ord('9')):
                    number += chr(c)
                    i += 1
                    c = ord(line[i])
                try:
                    value = int(number)
                except ValueError:
                    value = float(number)
                tokens.append(value)
            elif c in range(ord('A'), ord('z')):
                symbol = ''
                while c in range(ord('0'), ord('z')):
                    symbol += chr(c)
                    i += 1
                    c = ord(line[i])
                tokens.append(symbol)
            elif c == ord('\"'):
                string = ''
                i += 1
                c = ord(line[i])
                while c != ord('\"'):
                    string += chr(c)
                    i += 1
                    c = ord(line[i])
                tokens.append('\"' + string + '\"')
        except IndexError:
            break
        except EOFError:
            break
        i += 1

    return tokens


def evaluate(tree: list[str]) -> tuple[bool, Atom]:
    return True, eval(tree)


def string_representation(expr: object) -> str:
    if not isinstance(expr, list):
        return str(expr)
    else:
        return '('+' '.join(map(string_representation, expr))+')'


def repl() -> None:
    line = input("LISP>>")
    tokens = tokenize(line)
    ok, tree = abstract_syntax_tree(tokens)
    if not ok:
        print("Not a valid expression")
        return

    ok, result = evaluate(tree)
    if not ok:
        print("Couldn't complete evaluation!")
        return
    if result is not None:
        print(result)


def run_file(filename):
    with open(filename, 'r') as file:
        for line in file.readlines():
            tokens = tokenize(line)
            print("Tokens:" ,tokens)
            ok, tree = abstract_syntax_tree(tokens)
            print(tree)
            ok, result = evaluate(tree)
            if result is not None:
                print(result)


def banner():
    print("Welcome to my LISP Interpreter\nVersion:0.1\nPress 'Ctrl+C' to exit")


def main(args: list[str]) -> None:
    if len(args) > 0:
        for file in args:
            run_file(file)
            return None

    banner()
    while True:
        try:
            repl()
        except KeyboardInterrupt:
            print("\nExiting\n")
            break
        except:
            print("Something terrible happened!")
            traceback.print_exc()


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
