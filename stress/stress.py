'''
stress the CPU
'''

from subprocess import Popen, PIPE


if __name__ == '__main__':
    core = 12
    ps = []
    for i in range(core):
        command = ['python', 'run.py']
        p = Popen(command)

'''
i7-8700:
core | time(s) | freq(GHz) | power(W)
1    | 42      | 4.3       | 34
2    | 43      | 4.3       | 46
4    | 45      | 4.2       | 65
8    | 54-75   | 3.6       | 65 
12   | 101-107 | 3.5       | 65
'''
