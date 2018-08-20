'''
Matrix multiplication sample, some numba and CUDA testing code
'''
import math
import time
import numpy as np
from numba import cuda, jit, float64

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

@cuda.jit
def mat_mul_shared_kernal(A, B, C):
    '''matrix multiplication on gpu, optimized version using shared memory.
    '''
    s_A = cuda.shared.array((TPB, TPB), dtype=float64)  # s_ --> shared
    s_B = cuda.shared.array((TPB, TPB), dtype=float64)
    x, y = cuda.grid(2)
    tx = cuda.threadIdx.x
    ty = cuda.threadIdx.y
    bw = cuda.blockDim.x
    bh = cuda.blockDim.y
    #print((x, y), (tx, ty), (bx, by), (bw, bh))

    if x >= C.shape[0] or y >= C.shape[1]:
        return

    tmp = 0
    for i in range(int(A.shape[1]/TPB)):
        #print((x, y), (tx, ty), i)
        s_A[tx, ty] = A[x, ty + bw*i]
        s_B[tx, ty] = B[tx + bh*i, y]
        cuda.syncthreads()

        for j in range(TPB):
            tmp += s_A[tx, j] * s_B[j, ty]

        cuda.syncthreads()
    C[x, y] = tmp


def host_naive(A, B, C):
    '''host code for calling naive kernal
    '''
    d_A = cuda.to_device(A)  # d_ --> device
    d_B = cuda.to_device(B)
    d_C = cuda.device_array(C.shape, np.float64)

    threadsperblock = (TPB, TPB)
    blockspergrid_x = math.ceil(A.shape[0]/threadsperblock[0])
    blockspergrid_y = math.ceil(B.shape[1]/threadsperblock[1])
    blockspergrid = (blockspergrid_x, blockspergrid_y)

    mat_mul_naive_kernal[blockspergrid, threadsperblock](d_A, d_B, d_C)

    return d_C.copy_to_host()


def host_optimized(A, B, C):
    '''host code for calling naive kernal
    '''
    d_A = cuda.to_device(A)  # d_ --> device
    d_B = cuda.to_device(B)
    d_C = cuda.device_array(C.shape, np.float64)

    threadsperblock = (TPB, TPB)
    blockspergrid_x = math.ceil(A.shape[0]/threadsperblock[0])
    blockspergrid_y = math.ceil(B.shape[1]/threadsperblock[1])
    blockspergrid = (blockspergrid_x, blockspergrid_y)

    mat_mul_shared_kernal[blockspergrid, threadsperblock](d_A, d_B, d_C)

    return d_C.copy_to_host()


def main():
    '''main
    '''
    A = np.full((TPB*400, TPB*600), 0.5, dtype=np.float64)
    B = np.full((TPB*600, TPB*200), 2, dtype=np.float64)
    C = np.full((TPB*400, TPB*200), 0, dtype=np.float64)

    #start = time.time()
    #cpu_mat_mul_jit(A, B, C)
    #print('cpu mat mul numba.jit:', time.time()-start)

    #start = time.time()
    #cpu_mat_mul_jit(A, B, C)
    #print('cpu mat mul numba.jit:', time.time()-start)

    start = time.time()
    ans = host_naive(A, B, C)
    print('gpu mat mul global:', time.time()-start)
    print(ans)

    start = time.time()
    ans = host_naive(A, B, C)
    print('gpu mat mul global:', time.time()-start)

    start = time.time()
    ans = host_optimized(A, B, C)
    print('gpu mat mul shared:', time.time()-start)
    print(ans)

    start = time.time()
    ans = host_optimized(A, B, C)
    print('gpu mat mul shared:', time.time()-start)


if __name__ == '__main__':
    main()
