'''
Plot the famous Madnelbrot fractal
https://people.duke.edu/~ccc14/sta-663/CUDAPython.html
'''
import time
import matplotlib.pyplot as plt
import numpy as np
from numba import jit, cuda, uint32, float32


def mandel(x, y, max_iters):
    '''color function point at (x, y)
    '''
    c = complex(x, y)
    z = 0.0j
    for i in range(max_iters):
        z = z*z + c
        if z.real*z.real + z.imag*z.imag >= 4:
            return i
    return max_iters


def create_fractal(xmin, xmax, ymin, ymax, image, iters):
    '''create mandelbrot fractal
    '''
    height, width = image.shape
    pixel_size_x = (xmax - xmin)/width
    pixel_size_y = (ymax - ymin)/height

    for x in range(width):
        real = xmin + x*pixel_size_x
        for y in range(height):
            imag = ymin + y*pixel_size_y
            color = mandel(real, imag, iters)
            image[y, x] = color


def pure_python():
    gimage = np.zeros((1024, 1536), dtype=np.uint8)
    xmin, xmax, ymin, ymax = np.array([-2.0, 1.0, -1.0, 1.0]).astype('float32')
    iters = 100

    start = time.time()
    create_fractal(xmin, xmax, ymin, ymax, gimage, iters)
    print('Mandelbrot created on CPU in:', time.time()-start)
    #plt.imshow(gimage)
    #plt.savefig('mandelbrot.pdf')


mandel_numba = jit(mandel)

@jit
def create_fractal_numba(xmin, xmax, ymin, ymax, image, iters):
    '''create mandelbrot fractal with numba
    '''
    height, width = image.shape
    pixel_size_x = (xmax - xmin)/width
    pixel_size_y = (ymax - ymin)/height

    for x in range(width):
        real = xmin + x*pixel_size_x
        for y in range(height):
            imag = ymin + y*pixel_size_y
            color = mandel_numba(real, imag, iters)
            image[y, x] = color


def python_numba():
    gimage = np.zeros((1024, 1536), dtype=np.uint8)
    xmin, xmax, ymin, ymax = np.array([-2.0, 1.0, -1.0, 1.0]).astype('float32')
    iters = 100

    start = time.time()
    create_fractal_numba(xmin, xmax, ymin, ymax, gimage, iters)
    print('Mandelbrot created on CPU with numba in:', time.time()-start)

    start = time.time()
    create_fractal_numba(xmin, xmax, ymin, ymax, gimage, iters)
    print('Mandelbrot created on CPU with numba in:', time.time()-start)
    #plt.imshow(gimage)
    #plt.savefig('mandelbrot_numba.pdf')


@cuda.jit('float32(float32, float32, float32)', device=True, inline=True)
def mandel_gpu(x, y, max_iters):
    '''device function, color function point at (x, y)
    '''
    c = complex(x, y)
    z = 0.0j
    for i in range(max_iters):
        z = z*z + c
        if z.real*z.real + z.imag*z.imag >= 4:
            return i
    return max_iters

@cuda.jit
def create_fractal_kernal(xmin, xmax, ymin, ymax, image, iters):
    '''create mandelbrot fractal, cuda kernal
    '''
    height, width = image.shape
    #print(height, width)
    pixel_size_x = (xmax - xmin)/width
    pixel_size_y = (ymax - ymin)/height
    startX, startY = cuda.grid(2)
    gridX = cuda.gridDim.x * cuda.blockDim.x
    gridY = cuda.gridDim.y * cuda.blockDim.y
    #print('grid', startX, startY)

    for x in range(startX, width, gridX):
        real = xmin + x*pixel_size_x
        for y in range(startY, height, gridY):
            #print('x, y = ', x, y)
            imag = ymin + y*pixel_size_y
            color = mandel_gpu(real, imag, iters)
            image[y, x] = color


def cuda_host():
    gimage = np.zeros((1024, 1536), dtype=np.uint8)
    blockdim = (32, 8)
    griddim = (32, 16)
    xmin, xmax, ymin, ymax = np.array([-2.0, 1.0, -1.0, 1.0]).astype('float32')
    iters = 100

    start = time.time()
    d_image = cuda.to_device(gimage)
    create_fractal_kernal[griddim, blockdim](xmin, xmax, ymin, ymax, d_image, iters)
    gimage = d_image.copy_to_host()
    print('Mandelbrot created on GPU in:', time.time()-start)

    start = time.time()
    d_image = cuda.to_device(gimage)
    create_fractal_kernal[griddim, blockdim](xmin, xmax, ymin, ymax, d_image, iters)
    gimage = d_image.copy_to_host()
    print('Mandelbrot created on GPU in:', time.time()-start)
    #plt.imshow(gimage)
    #plt.savefig('mandelbrot_cuda.pdf')


def main():
    '''main function
    '''
    pure_python()
    python_numba()
    cuda_host()


if __name__ == '__main__':
    main()
