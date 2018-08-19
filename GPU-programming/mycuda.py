'''
Matrix multiplication sample, some numba and CUDA testing code
'''
import math
import time
import numpy as np
from numba import cuda, jit

TPB = 32 # thread per block

def cpu_mat_mul(A, B, C):
    '''matrix mulplication on cpu, O(n^3) implementation
    '''
    for i in range(C.shape[0]):
        for j in range(C.shape[1]):
            summation = 0
            for k in range(A.shape[1]):
                summation += A[i, k] * B[k, j]
            C[i, j] = summation

@jit
def cpu_mat_mul_jit(A, B, C):
    '''matrix mulplication on cpu O(n^3) implementation with @jit decocation
    '''
    for i in range(C.shape[0]):
        for j in range(C.shape[1]):
            summation = 0
            for k in range(A.shape[1]):
                summation += A[i, k] * B[k, j]
            C[i, j] = summation

@cuda.jit
def mat_mul_naive_kernal(A, B, C):
    '''matrix multiplication on gpu, naive method using global device memory
    '''
    i, j = cuda.grid(2)
    if i < C.shape[0] and j < C.shape[1]:
        summation = 0
        for k in range(A.shape[1]):
            summation += A[i, k] * B[k, j]
        C[i, j] = summation


def host_naive(A, B, C):
    '''host code for calling naive kernal
    '''
    d_A = cuda.to_device(A)
    d_B = cuda.to_device(B)
    d_C = cuda.device_array(C.shape, np.float64)

    threadsperblock = (TPB, TPB)
    blockspergrid_x = math.ceil(A.shape[1]/threadsperblock[0])
    blockspergrid_y = math.ceil(A.shape[0]/threadsperblock[1])
    blockspergrid = (blockspergrid_x, blockspergrid_y)

    mat_mul_naive_kernal[blockspergrid, threadsperblock](d_A, d_B, d_C)
    C = d_C.copy_to_host()


def main():
    '''main
    '''
    A = np.full((TPB*20, TPB*30), 0.5, dtype=np.float64)
    B = np.full((TPB*30, TPB*10), 2, dtype=np.float64)
    C = np.full((TPB*20, TPB*10), 0, dtype=np.float64)
    #start = time.time()
    #cpu_mat_mul(A, B, C)
    #print('cpu mat mul:', time.time()-start)

    start = time.time()
    cpu_mat_mul_jit(A, B, C)
    print('cpu mat mul numba.jit:', time.time()-start)

    start = time.time()
    cpu_mat_mul_jit(A, B, C)
    print('cpu mat mul numba.jit:', time.time()-start)

    start = time.time()
    host_naive(A, B, C)
    print('cpu mat mul cuda.jit:', time.time()-start)

    start = time.time()
    host_naive(A, B, C)
    print('cpu mat mul cuda.jit:', time.time()-start)


if __name__ == '__main__':
    main()
