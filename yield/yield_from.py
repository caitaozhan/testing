from itertools import chain
import time

def average():
    total = 0
    count = 0
    avg = None
    while True:
        num = yield avg
        total += num
        count += 1
        avg = total / count

def wrap_average(generator):
    yield from generator

def wrapper(wrap):
    print(next(wrap))     # start the generator
    print(wrap.send(10))  # 10
    print(wrap.send(20))  # 15
    print(wrap.send(30))  # 20
    print(wrap.send(40))  # 25


def generator():
    for i in range(10):
        yield i
    for j in range(10, 20):
        yield j

def generator2():
    for i in range(10):
        yield i

def generator3():
    for j in range(10, 20):
        yield j

def generator4():
    yield from generator2()
    yield from generator3()

def generator5():
    for v in chain(generator2(), generator3()):
        yield v

def generator6():
    while True:
        yield 1
        time.sleep(0.2)

def generator7():
    while True:
        yield 'a'
        time.sleep(0.2)

def generator8():
    # yield from generator6()
    # yield from generator7()
    for i in chain(generator6(), generator7()):
        yield i


def main1():
    g = average()
    wrap = wrap_average(g)
    wrapper(wrap)

def main2():
    '''same output as main4, without the use of wrapper
    '''
    g = average()
    print(next(g))
    print(g.send(10))
    print(g.send(20))
    print(g.send(30))
    print(g.send(40))

def main3():
    g = generator()
    for i in g:
        print(i, end=' ')
    print('\n*****')

    g = generator4()
    for i in g:
        print(i, end=' ')
    print('\n*****')
    
    g = generator5()
    for i in g:
        print(i, end=' ')
    print('\n*****')

def main4():
    '''never able to reach generator7, because generator6 is infinity loop
    '''
    g = generator8()
    for i in g:
        print(i, end=' ')
    


if __name__ == '__main__':
    # main1()
    # print('\n' + "#"*20 + '\n')
    # main2()
    # print('\n' + "#"*20 + '\n')
    # main3()
    main4()
