from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit.visualization import plot_histogram
from qiskit import Aer, execute

import sys
sys.path.append('.')
from DQCS import DistributedCircuits

if __name__ == '__main__':
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.h(1)
    qc.cx(0, 2)
    nodes = {"1": [0, 1], "2": [2]}
    print(qc)
    gate_app, circuit = DistributedCircuits(qc, nodes).create_circuit()
    print(gate_app)
    print(circuit)

