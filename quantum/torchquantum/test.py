import random

import torch
import torchquantum as tq
import numpy as np
import matplotlib.pyplot as plt

from typing import Union, List
from collections import Counter, OrderedDict



def gen_bitstrings(n_wires):
    return ['{:0{}b}'.format(k, n_wires) for k in range(2**n_wires)]


def measure(q_state, n_shots=1024, draw_id=None):
    """Measure the target state and obtain classical bitstream distribution

    Args:
        q_state: input tq.QuantumState
        n_shots: number of simulated shots
        draw_id: which state to draw

    Returns:
        distribution of bitstrings

    """
    bitstring_candidates = gen_bitstrings(q_state.n_wires)

    state_mag = q_state.get_states_1d().abs().detach().numpy()
    distri_all = []

    for state_mag_one in state_mag:
        state_prob_one = np.abs(state_mag_one) ** 2
        measured = random.choices(
            population=bitstring_candidates,
            weights=state_prob_one,
            k=n_shots,
        )
        counter = Counter(measured)
        counter.update({key: 0 for key in bitstring_candidates})
        distri = dict(counter)
        distri = OrderedDict(sorted(distri.items()))
        distri_all.append(distri)

    if draw_id is not None:
        plt.bar(distri_all[draw_id].keys(), distri_all[draw_id].values())
        plt.xticks(rotation='vertical')
        plt.xlabel('bitstring [qubit0, qubit1, ..., qubitN]')
        plt.title('distribution of measured bitstrings')
        plt.show()
    return distri_all



def expval(q_device: tq.QuantumDevice,
           wires: Union[int, List[int]],
           observables: Union[tq.Observable, List[tq.Observable]]):

    all_dims = np.arange(q_device.states.dim())
    if isinstance(wires, int):
        wires = [wires]
        observables = [observables]

    # rotation to the desired basis
    for wire, observable in zip(wires, observables):
        for rotation in observable.diagonalizing_gates():
            rotation(q_device, wires=wire)

    states = q_device.states
    # compute magnitude
    state_mag = torch.abs(states) ** 2

    expectations = []
    for wire, observable in zip(wires, observables):
        # compute marginal magnitude
        reduction_dims = np.delete(all_dims, [0, wire + 1])
        if reduction_dims.size == 0:
            probs = state_mag
        else:
            probs = state_mag.sum(list(reduction_dims))
        res = probs.mv(observable.eigvals.real.to(probs.device))
        expectations.append(res)

    return torch.stack(expectations, dim=-1)


class MeasureAll(tq.QuantumModule):
    def __init__(self, obs, v_c_reg_mapping=None):
        super().__init__()
        self.obs = obs
        self.v_c_reg_mapping = v_c_reg_mapping

    def forward(self, q_device: tq.QuantumDevice):
        self.q_device = q_device
        x = expval(q_device, list(range(q_device.n_wires)), [self.obs()] * q_device.n_wires)

        if self.v_c_reg_mapping is not None:
            c2v_mapping = self.v_c_reg_mapping['c2v']
            """
            the measurement is not normal order, need permutation 
            """
            perm = []
            for k in range(x.shape[-1]):
                if k in c2v_mapping.keys():
                    perm.append(c2v_mapping[k])
            x = x[:, perm]

        if self.noise_model_tq is not None and self.noise_model_tq.is_add_noise:
            return self.noise_model_tq.apply_readout_error(x)
        else:
            return x

    def set_v_c_reg_mapping(self, mapping):
        self.v_c_reg_mapping = mapping


def measurement(q_state):
    '''tq.measure()
    '''
    bitstring = measure(q_state, n_shots=1000, draw_id=0)
    print(bitstring)


def measure_all(q_state):
    '''tq.MeasureAll
    '''
    measure = MeasureAll(tq.PauliZ)
    result = measure(q_state)
    print(result)


def main():
    q_state = tq.QuantumState(n_wires=3)
    print(f'0: {q_state}\n')
    q_state.x(wires=1)
    q_state.rx(wires=2, params=0.6 * np.pi)
    q_state.ry(wires=0, params=0.3 * np.pi)
    q_state.qubitunitary(wires=1, params=[[0, 1j], [-1j, 0]])
    q_state.cnot(wires=[0, 1])
    print(f'1: {q_state}\n')

    measurement(q_state)

    measure_all(q_state)



if __name__ == '__main__':
    main()
