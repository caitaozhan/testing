import math
import numpy as np
from numba import cuda
from cuda_kernals import matmul_kernal


TPB = 16


def main():
    '''main
    '''
    A = np.full((TPB*20, TPB*30), 3, dtype=np.float64)
    B = np.full((TPB*30, TPB*10), 4, dtype=np.float64)

    d_A = cuda.to_device(A)
    d_B = cuda.to_device(B)
    d_C = cuda.device_array((TPB*20, TPB*10), dtype=np.float64)

    threadsperblock = (TPB, TPB)
    blockspergrid_x = math.ceil(A.shape[0]/threadsperblock[0])
    blockspergrid_y = math.ceil(A.shape[1]/threadsperblock[1])
    blockspergrid = (blockspergrid_x, blockspergrid_y)

    matmul_kernal[blockspergrid, threadsperblock](d_A, d_B, d_C)

    C = d_C.copy_to_host()
    print(C)


if __name__ == '__main__':
    main()
    