from numba import cuda


@cuda.jit('void(float64[:,:], float64[:,:], float64[:,:])')
def matmul_kernal(A, B, C):
    '''matrix multiplication
    '''
    x, y = cuda.grid(2)
    if x < C.shape[0] and y < C.shape[1]:
        summation = 0.
        for i in range(A.shape[1]):
            summation += A[x, i] * B[i, y]
        C[x, y] = summation
    