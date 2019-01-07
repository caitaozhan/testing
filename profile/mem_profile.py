from scipy.stats import multivariate_normal
import numpy as np

@profile
def my_func():
    a = [1] * (10**6)
    b = [2] * (2*10**7)
    del b
    return a

@profile
def multivariate():
    mymean = np.random.randn(1000)
    mycov = np.zeros(1000000).reshape(1000, 1000)
    for i in range(1000):
        mycov[i, i] = 1
    mylist = []
    for _ in range(100):
        mylist.append(multivariate_normal(mean=mymean, cov=mycov))
    del mylist


@profile
def numpy_ndarray(sensor, hypothesis, binnum):
    ndarray = np.random.rand(sensor, hypothesis, binnum)
    del ndarray


if __name__ == '__main__':
    #my_func()
    #my_func()
    #multivariate()
    numpy_ndarray(4096, 1000, 1000)

# in command line: python -m memory_profiler mem_profile.py
