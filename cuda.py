import math
from numba import vectorize, cuda
import numpy as np



@cuda.jit
def my_kernal(io_array):
    #tx = cuda.threadIdx.x   # thread id in a 1D block
    #ty = cuda.blockIdx.x    # block id in a 1D grid
    #bw = cuda.blockDim.x    # block width, i.e. number of threads per block
    #pos = tx + ty*bw        # compute flattened index inside the array
    #print(tx, ty, bw, pos)
    pos = cuda.grid(1)
    if pos < io_array.size: # check array boundaries
        io_array[pos] *= 2  # do the computation


@vectorize(['float64(float64,float64)'], target='cpu')
def add(a, b):
    return a + b


def test1():
    data = np.ones(256)
    threadsperblock = 256
    blockspergrid = math.ceil(data.shape[0]/threadsperblock)
    my_kernal[blockspergrid, threadsperblock](data)
    print(data)


def test2():
    N = 100000
    A = np.ones(N, dtype=np.float64)
    B = np.ones(N, dtype=np.float64)
    C = np.zeros_like(A, dtype=np.float64)
    C = add(A, B)
    print(C)


if __name__ == '__main__':
    test1()
    test2()
