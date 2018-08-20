import math
import time
import numpy as np
from numba import vectorize, cuda, float64



#@cuda.jit
def my_kernal(io_array):
    #tx = cuda.threadIdx.x   # thread id in a 1D block
    #ty = cuda.blockIdx.x    # block id in a 1D grid
    #bw = cuda.blockDim.x    # block width, i.e. number of threads per block
    #pos = tx + ty*bw        # compute flattened index inside the array
    #print(tx, ty, bw, pos)
    pos = cuda.grid(1)
    if pos < io_array.size: # check array boundaries
        io_array[pos] *= 2  # do the computation


@vectorize([float64(float64, float64)], target='cpu')
def add_vec_cpu(a, b):
    return a + b


@vectorize(['float64(float64,float64)'], target='cuda')
def add_vec_cuda(a, b):
    return a + b


@vectorize(['float64(float64, float64)'], target='cpu')
def cpu_sincos(x, y):
    return math.sin(x) * math.cos(y)


@vectorize([float64(float64, float64)], target='cuda')
def gpu_sincos(x, y):
    return math.sin(x) * math.cos(y)


@vectorize([float64(float64, float64, float64, float64)])
def cpu_powers(p, q, r, s):
    return math.sqrt(p**2 + q**3 + r**4 + s**5)


@vectorize([float64(float64, float64, float64, float64)], target='cuda')
def gpu_powers(p, q, r, s):
    return math.sqrt(p**2 + q**3 + r**4 + s**5)


def test1():
    data = np.ones(256)
    threadsperblock = 256
    blockspergrid = math.ceil(data.shape[0]/threadsperblock)
    my_kernal[blockspergrid, threadsperblock](data)
    print(data)


def test2():
    N = 100000000
    A = np.ones(N, dtype=np.float64)
    B = np.ones(N, dtype=np.float64)
    C = np.zeros(N, dtype=np.float64)
    start = time.time()
    C = add_vec_cuda(A, B)
    print(time.time()-start)


def test3():
    N = 100000000
    A = np.ones(N, dtype=np.float64)
    B = np.ones(N, dtype=np.float64)
    C = np.zeros(N, dtype=np.float64)
    start = time.time()
    C = add_vec_cpu(A, B)
    print(time.time()-start)


def test4():
    n = 1000000
    x = np.arange(n, dtype=np.float64)
    y = np.arange(n, dtype=np.float64)

    np_ans = np.sin(x) * np.cos(y)
    nb_cpu_ans = cpu_sincos(x, y)
    nb_gpu_ans = gpu_sincos(x, y)

    print("CPU vectorize:", np.allclose(nb_cpu_ans, np_ans))
    print("CPU vectorize:", np.allclose(nb_gpu_ans, np_ans))


def test5():
    n = 10000000
    x = np.arange(n, dtype=np.float64)
    y = np.arange(n, dtype=np.float64)
    z = np.zeros(n, dtype=np.float64)
    start = time.time()
    z = cpu_sincos(x, y)
    print(time.time()-start)


def test6():
    n = 10000000
    x = np.arange(n, dtype=np.float64)
    y = np.arange(n, dtype=np.float64)
    z = np.zeros(n, dtype=np.float64)
    start = time.time()
    z = gpu_sincos(x, y)
    print(time.time()-start)


def test7():
    n = 10000000
    x = np.arange(n, dtype=np.float64)
    y = np.arange(n, dtype=np.float64)
    z = np.zeros(n, dtype=np.float64)
    start = time.time()
    np_ans = np.sin(x) * np.cos(y)
    print(time.time()-start)


def test8():
    n = 5000000
    p = np.random.random(n).astype(np.float64)
    q = np.random.random(n).astype(np.float64)
    r = np.random.random(n).astype(np.float64)
    s = np.random.random(n).astype(np.float64)
    for i in range(10):
        start = time.time()
        np.sqrt(p**2 + q**3 + r**4 + s**5)
        print(time.time()-start)

def test9():
    n = 5000000
    p = np.random.random(n).astype(np.float64)
    q = np.random.random(n).astype(np.float64)
    r = np.random.random(n).astype(np.float64)
    s = np.random.random(n).astype(np.float64)
    for i in range(500):
        start = time.time()
        cpu_powers(p, q, r, s)
        print(time.time()-start)

def test10():
    n = 5000000
    p = np.random.random(n).astype(np.float64)
    q = np.random.random(n).astype(np.float64)
    r = np.random.random(n).astype(np.float64)
    s = np.random.random(n).astype(np.float64)
    for i in range(500):
        start = time.time()
        gpu_powers(p, q, r, s)
        print(time.time()-start)


if __name__ == '__main__':
    #test1()
    #for i in range(50):
    #    test2()
    #print('*****')
    #for i in range(50):
    #    test3()
    test8()
    print('\n\n\n')
    test9()
    print('\n\n\n')
    test10()
