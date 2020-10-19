'''
stress the CPU
'''

from subprocess import Popen, PIPE


if __name__ == '__main__':
    task = 4
    ps = []
    for i in range(task):
        command = ['python', 'run.py']
        p = Popen(command)

'''

Lenovo
i5-3230M (2 core, 4 hyperthread)
task | time(s) | freq(GHz) | power(W)
1    | 101     | 3.2       | 11
2    | 107     | 3.0       | 14 
4    | 192     | 3.0       | 15

Acer
i5-4200U (2 core, 4 hyperthread)
task | time(s) | freq(GHz) | power(W)
1    | 77      | 2.3       | 11
2    | 86      | 2.3       | 15
4    | 167     | 2.3       | 16

Thinkpad P50
i7-6700HQ (4 core, 8 hyperthread)
task | time(s) | freq(GHz) | power(W)
1    | 49      | 3.5       | 18
2    | 52      | 3.3       | 26
4    | 55      | 3.1       | 42
6    | 85      | 3.1       | 43
8    | 108     | 3.1       | 44

ABS Desktop
i7-8700 (6 core, 12 hyperthread)
task | time(s) | freq(GHz) | power(W)
1    | 42      | 4.3       | 34
2    | 43      | 4.3       | 46
4    | 45      | 4.2       | 65
6    | 53      | 3.7       | 65  
8    | 75      | 3.6       | 65 
12   | 107     | 3.5       | 65

HP laptop
i5-1035G1 (4 core, 8 hyperthread)
task | time(s) | freq(GHz) | power(W)
1    | 50      | 3.3       | 11
2    | 55      | 2.9       | 14
4    | 73      | 2.1       | 15
6    | 107     | 1.9       | 15
8    | 141     | 1.9       | 15

'''
