'''http://unixnme.blogspot.com/2017/10/thread-safe-generators-in-python.html
'''

import threading
import multiprocessing.pool as mp
import time
import random

class thread_safe_generator:
    def __init__(self, gen):
        self.gen = gen
        self.lock = threading.Lock()
    
    def __iter__(self):
        return self

    def __next__(self):
        with self.lock:
            return next(self.gen)  # resume to the yield expression in the generator

def simple_generator(id):
    i = 0
    while True:
        yield f'id={id},i={i}'
        i += 1
        time.sleep(random.random())

def thread_safe(f):
    def g(*args, **kwargs):
        return thread_safe_generator(f(*args, **kwargs))
    return g

@thread_safe
def simple_generator2(id):
    i = 0
    while True:
        yield f'id={id},i={i}'
        i += 1
        time.sleep(random.random())



def main0():
    # when using yield from, main0 also becomes a generator
    gen = thread_safe_generator(simple_generator(0))
    yield from gen

def generator_caller(gen):
    '''a caller that calls (the next function) the generator
    '''
    while True:
        print(next(gen))

def main1():
    # single thread, five task, only the first task will execute. the first task will block the others
    for i in range(5):
        gen = thread_safe_generator(simple_generator(i))
        generator_caller(gen)

def main2():
    # five threads, five tasks, all five tasks will execute concurrently in macroscale, but sequencially in microscale
    pool = mp.ThreadPool(5)
    for i in range(5):
        gen = thread_safe_generator(simple_generator(i))
        pool.apply_async(generator_caller, (gen,))
    pool.close()
    pool.join()

def main3():
    gen = simple_generator2(0)
    generator_caller(gen)

def main4():
    pool = mp.ThreadPool(5)
    for i in range(5):
        gen = simple_generator2(i)
        pool.apply_async(generator_caller, (gen,))
    pool.close()
    pool.join()


if __name__ == '__main__':
    # generator_caller(main0())

    # main1()

    # main2()

    # main3()

    main4()
