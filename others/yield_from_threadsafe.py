'''https://anandology.com/blog/using-iterators-and-generators/
'''

import threading


def count():
    '''this is a generator
    '''
    i = 0
    while True:
        i += 1
        yield i


class threadsafe_generator:
    '''takes an generator and makes it thread-safe by 
       serializing call to the `next` method of given iterator/generator
    '''
    def __init__(self, gen):
        self.gen = gen
        self.lock = threading.Lock()
    
    def __iter__(self):
        return self
    
    def next(self):
        with self.lock:
            return self.gen.__next__()


def threadsafe_generator_decorator(f):
    '''a decorator that takes a generator function and makes it thread safe
    '''
    def g(*args, **kwargs):
        return threadsafe_generator(f(*args, **kwargs))
    return g


@threadsafe_generator_decorator
def count2():
    i = 0
    while True:
        i += 1
        yield i


class Counter:
    '''a Python iterator object must implement two special methods, __iter__ and __next__
       collectively called the iterator protocol
    '''
    def __init__(self):
        self.i = 0
        self.lock = threading.Lock()
    
    def __iter__(self):
        return self
    
    def next(self):
        # acquire/release the lock when updating self.i
        with self.lock:
            self.i += 1
            return self.i


def loop(func, n):
    '''runs the given function n times in a loop
    '''
    for _ in range(n):
        func()


def run(f, repeats=1000, nthreads=10):
    '''starts multiple threads to execute the fiven function multiple times in each thread
    '''
    # create threads
    threads = [threading.Thread(target=loop, args=(f, repeats)) for i in range(nthreads)]

    # start threads
    for t in threads:
        t.start()

    # wait for threads to finish
    for t in threads:
        t.join()


def main():
    c1 = count()
    c2 = Counter()

    # call c1.next 100K times in 2 different threads
    run(c1.__next__, repeats=100000, nthreads=4)
    print('c1', c1.__next__())

    # call c2.next 100K times in 2 different threads
    run(c2.next, repeats=100000, nthreads=4)
    print('c2', c2.next())


def main2():
    c1 = count()
    c1 = threadsafe_generator(c1)
    run(c1.next, repeats=100000, nthreads=4)
    print('c1', c1.next())

    c2 = count2()
    run(c2.next, repeats=100000, nthreads=4)
    print('c2', c2.next())


if __name__ == '__main__':
    # main()
    main2()
