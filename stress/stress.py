'''
stress the CPU
'''

from subprocess import Popen, PIPE


if __name__ == '__main__':
    core = 4
    ps = []
    for i in range(core):
        command = ['python', 'run.py']
        p = Popen(command)
