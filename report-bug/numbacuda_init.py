import numpy as np
from numba import cuda, float64

local_array_size = 1

def update_size(size):
    global local_array_size
    local_array_size = size

@cuda.jit('void(float64[:])')  # if not use explicit signature, then the update_size method works.
def kernal(array):
    x = cuda.grid(1)
    local_array = cuda.local.array(local_array_size, dtype=float64)
    for i in range(local_array_size):
        local_array[i] = i
    array[x] = local_array[local_array_size-1]

d_array = cuda.device_array(32, np.float64)
threadsperblock = 32
blockspergrid = 1
update_size(10)

kernal[blockspergrid, threadsperblock](d_array)

print(d_array.copy_to_host())
