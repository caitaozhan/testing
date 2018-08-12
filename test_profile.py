import line_profiler

@profile
def slow(N=1000000):
    total = 0
    for i in range(N):
        total += i
    return total


def hehe(N=1000000):
    total = sum(range(N))
    return total

@profile
def pythonic(N=1000000):
    total = sum(range(N))
    return total

if __name__ == '__main__':
    slow()
    hehe()
    pythonic()
