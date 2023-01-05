from interpreter import eval, tokenize, abstract_syntax_tree, add_globals, Env
global_env = add_globals(Env())


def valid():
    def run(expr): return eval(abstract_syntax_tree(
        tokenize(expr))[1], env=global_env)

    cases = {"(+ 1 2)": 3,
             "(- 2 1)": 1,
             "(/ 2 2)": 1,
             "(* 3 2)": 6,
             "(+ 1 2)": 3,
             "(+ 1 2)": 3,
             "(+ 1 2)": 3}
    success = 0
    for expr, value in cases.items():
        if run(expr) == value:
            success += 1
        else:
            print(f"[FAILED] '{expr}' != '{value}', got '{run(expr)}'")
    return success / len(cases)


if __name__ == '__main__':
    print(f"Passed: {valid()*100:.1f}%")
