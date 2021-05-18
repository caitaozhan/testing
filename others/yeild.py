''' at first glance, yield is similar to return, 
    but a return completely ceases a function, whereas yield interrupts a peice of code and will come back later (coroutine)
    yield makes a function not a function anymore, it becomes a generator.

https://en.cppreference.com/w/cpp/language/coroutines
Coroutine: a coroutine is a function that can suspend execution to be resumed later. Coroutines are stackless: they suspend
execution by returning to the caller and the data that is required to resume execution is stored separately from the stack.
This allows for sequential code that executes asynchronously (e.g. handle non-blocking I/O without explicit callbacks), and
also supports algorithms on lazy-computed infinite sequences and other uses.

'''
from types import FunctionType, GeneratorType

def foo():
    print("starting...")
    while True:
        res = yield 4
        print("res:",res)

g = foo()
print(next(g))
print("*"*20)
print(next(g))

print("#"*20)

def bar():
    print("starting...")
    while True:
        res = yield 4
        print("res:",res)

g = bar()
print(next(g))
print("*"*20)
print(g.send(7))

print("#"*20)

def fib(max):
    n, a, b = 0, 0, 1
    while n < max:
        yield b
        a, b = b, a + b
        n += 1

print('fib    Iterable:', isinstance(fib, GeneratorType))
print('fib    Function:', isinstance(fib, FunctionType))
print('fib(5) Iterable:', isinstance(fib(5), GeneratorType))

for n in fib(5):
    print(n)
