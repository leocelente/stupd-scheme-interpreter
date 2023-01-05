# Stupid Scheme Interpreter
My language playground based around Peter Norvig's [simplest LISP interpreter](http://norvig.com/lispy.html), well described in Michael Nielsen's [Lisp as the Maxwell’s equations of software](https://michaelnielsen.org/ddi/lisp-as-the-maxwells-equations-of-software/)

It's a very simple Scheme interpreter, not well structured and it lacks a lot of things. What I added from the base implementation given by Norvig was string support through a more complex tokenizer.

It has a REPL and reads files.

It may be very unsophisticated but it can calculate Fibonacci:
```scheme
LISP>>(define fib (lambda (n) (if (< n 3) 1 (+ (fib (- n 1)) (fib (- n 2))))))
LISP>>(fib 12)
144
```

What it currently lacks is any multiline support, so color-coded parenthesis is a must hahah.
Currently the goal is to improve the interpreter. In the future some form of backend may be implemented.
