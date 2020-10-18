'''
stress the CPU
'''

from subprocess import Popen, PIPE


if __name__ == '__main__':
    core = 6
    ps = []
    for i in range(core):
        command = ['python', 'run.py']
        p = Popen(command)

'''

i7-8700 (6 core, 12 hyperthread)
core | time(s) | freq(GHz) | power(W)
1    | 42      | 4.3       | 34
2    | 43      | 4.3       | 46
4    | 45      | 4.2       | 65
6    | 53      | 3.7       | 65  
8    | 75      | 3.6       | 65 
12   | 107     | 3.5       | 65


i5-1035G1 (4 core, 8 hyperthread)
core | time(s) | freq(GHz) | power(W)
1    | 50      | 3.3       | 11
2    | 55      | 2.9       | 14
4    | 73      | 2.1       | 15
6    | 107     | 1.9       | 15
8    | 141     | 1.9       | 15


'''
