'''
from the book <<Effective Python>> item 34
'''

import math

def wave_modulating(steps):
    step_size = 2 * math.pi / steps
    amplitude = yield
    for step in range(steps):
        radians = step * step_size
        fraction = math.sin(radians)
        output = amplitude * fraction
        amplitude = yield output


def complex_wave_modulating():
    yield from wave_modulating(3)
    yield from wave_modulating(4)
    yield from wave_modulating(5)


def transmit(output):
    if output is None:
        print(f'Output is None')
    else:
        print(f'Output: {output:>5.1f}')


def run_modulating(it):
    amplitudes = [None, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    for amplitude in amplitudes:
        output = it.send(amplitude)
        transmit(output)


# run_modulating(wave_modulating(12))

# run_modulating(complex_wave_modulating())


def wave_cascading(amplitude_it, steps):
    step_size = 2 * math.pi / steps
    for step in range(steps):
        radians = step * step_size
        fraction = math.sin(radians)
        amplitude = next(amplitude_it)
        output = amplitude * fraction
        yield output


def complex_wave_cascading(amplitude_it):
    yield from wave_cascading(amplitude_it, 3)
    yield from wave_cascading(amplitude_it, 4)
    yield from wave_cascading(amplitude_it, 5)


def run_cascading():
    amplitudes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    it = complex_wave_cascading(iter(amplitudes))
    for amplitude in amplitudes:
        output = next(it)
        transmit(output)

run_cascading()
