import time
import numpy as np
from numba import cuda


@cuda.reduce
def sum_reduce(a, b):
    return a + b


@cuda.reduce
def prod_reduce(a, b):
    return a*b


def main():
    '''main
    '''
    A = np.arange(1, 5, dtype=np.float64)

    start = time.time()
    expect = A.sum()
    print('time for numpy:', time.time()-start)
    print(expect)

    start = time.time()
    got = sum_reduce(A)
    print('time for cuda reduce:', time.time()-start)
    print(got)

    start = time.time()
    got = sum_reduce(A)
    print('time for cuda reduce:', time.time()-start)

    print('\n#####################\n')

    start = time.time()
    expect = A.prod()
    print('time for numpy:', time.time()-start)
    print(expect)

    print(A)
    start = time.time()
    got = prod_reduce(A)
    print('time for cuda reduce:', time.time()-start)
    print(got)

    start = time.time()
    got = prod_reduce(A)
    print('time for cuda reduce:', time.time()-start)


if __name__ == '__main__':
    main()
