'''A time consuming task
'''

import numpy as np

def cpu_mat_mul(A, B, C):
    '''matrix mulplication on cpu, O(n^3) implementation
    '''
    for i in range(C.shape[0]):
        for j in range(C.shape[1]):
            summation = 0
            for k in range(A.shape[1]):
                summation += A[i, k] * B[k, j]
            C[i, j] = summation


def task():
    TPB = 120
    A = np.full((TPB*4, TPB*6), 0.5, dtype=np.float64)
    B = np.full((TPB*6, TPB*2), 2, dtype=np.float64)
    C = np.full((TPB*4, TPB*2), 0, dtype=np.float64)
    cpu_mat_mul(A, B, C)
    return np.sum(C)


if __name__ == '__main__':
    print(task())