import line_profiler
import memory_profiler
import numpy as np
import copy

@profile
def slow(N=1000000):
    total = 0
    for i in range(N):
        total += i
    return total


def hehe(N=1000000):
    total = sum(range(N))
    return total


@profile
def pythonic(N=1000000):
    total = sum(range(N))
    return total


@profile
def my_func():
    a = [1] * (10**6)
    b = [2] * (2*10**7)
    del b
    return a


@profile
def bubblesort(X2):
    X = copy.deepcopy(X2)
    N = len(X)
    for end in range(N, 1, -1):
        for i in range(end - 1):
            cur = X[i]
            if cur > X[i + 1]:
                tmp = X[i]
                X[i] = X[i + 1]
                X[i + 1] = tmp

                
@profile
def bubblesort2(X2):
    X = copy.deepcopy(X2)
    N = len(X)
    for end in range(N, 1, -1):
        for i in range(end - 1):
            if X[i] > X[i + 1]:
                tmp = X[i]
                X[i] = X[i + 1]
                X[i + 1] = tmp

                
if __name__ == '__main__':
    X = np.random.randn(1000)
    bubblesort(X)
    bubblesort2(X)
    '''
    slow()
    hehe()
    pythonic()
    my_func()
    '''
