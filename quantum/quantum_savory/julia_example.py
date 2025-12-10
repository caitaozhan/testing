import numpy as np
from juliacall import Main as jl
from sequence.kernel.timeline import Timeline
from sequence.components.memory import Memory
from sequence.topology.router_net_topo import RouterNetTopo

jl.seval("using QuantumSavory")
jl.seval("using QuantumSavory.StatesZoo")

def stateszoo():
    jl.seval("using QuantumSavory")
    jl.seval("using QuantumSavory.StatesZoo")

    etaA = 0.5  # Individual channel transmissivity from source A to entanglement swapping station
    etaB = 0.5  # Individual channel transmissivity from source B to entanglement swapping station
    Pd   = 0.01 # Total excess noise (photons per qubit slot) in photon detectors
    etaD = 0.85 # Detection efficiency of photon detectors
    V    = 0.95 # Mode matching parameter for individual interacting photonic pulses with `|V|` evaluates mode overlap and `arg(V)` evaluates the carrier phase mismatch, |V|∈[0,1]
    m    = 0    # A single parity bit determined by the click pattern (m = 0 for [0, 1, 1, 0] or [1, 0, 0, 1]; m = 1 for [1, 1, 0, 0] or [0, 0, 1, 1])

    bk = jl.BarrettKokBellPair(etaA, etaB, Pd, etaD, V, m)
    print(f"Barret-Kok Bell pair (normalized): {bk}")

    rho_qo = jl.QuantumSavory.express(bk, jl.QuantumSavory.QuantumOpticsRepr())
    print("QuantumOptics operator:")
    print(rho_qo)

    rho_np = np.array(rho_qo.data)
    print("\nDensity matrix as NumPy array:")
    print(rho_np)


def get_density_matrix_from_qsavory(etaA, etaB, Pd, etaD, V, m) -> np.ndarray:
    """
    Docstring for get_density_matrix_from_qsavory
    Args:
        etaA (float): Individual channel transmissivity from source A to entanglement swapping station
        etaB (float): Individual channel transmissivity from source B to entanglement swapping station
        Pd (float): Total excess noise (photons per qubit slot) in photon detectors
        etaD (float): Detection efficiency of photon detectors
        V (float): Mode matching parameter for individual interacting photonic pulses with `|V|` evaluates mode overlap and `arg(V)` evaluates the carrier phase mismatch, |V|∈[0,1]
        m (int): A single parity bit determined by the click pattern (m = 0 for [0, 1, 1, 0] or [1, 0, 0, 1]; m = 1 for [1, 1, 0, 0] or [0, 0, 1, 1])
    
    Returns:
        np.ndarray: the density matrix as a NumPy array
    """
    # jl.seval("using QuantumSavory")
    # jl.seval("using QuantumSavory.StatesZoo")

    bk = jl.BarrettKokBellPair(etaA, etaB, Pd, etaD, V, m)
    rho_qo = jl.QuantumSavory.express(bk, jl.QuantumSavory.QuantumOpticsRepr())
    rho_np = np.array(rho_qo.data)
    return rho_np


def entangle_memory(tl: Timeline, memo1: Memory, memo2: Memory, density_matrix: np.ndarray):
    """
    Docstring for entangle_memory
    
    Args:
        tl (Timeline): the simulation timeline
        memo1 (Memory): the first memory component
        memo2 (Memory): the second memory component
        density_matrix (np.ndarray): the density matrix to set
    """
    memo1.reset()
    memo2.reset()
    tl.quantum_manager.set([memo1.qstate_key, memo2.qstate_key], density_matrix)
    memo1.entangled_memory['memo_id'] = memo2.name
    memo2.entangled_memory['memo_id'] = memo1.name
    # memo1.fidelity = memo2.fidelity = fidelity


def stateszoo2sequence():

    # step 1: initialize the quantum network
    config_file = "line_2.json"
    network_topo = RouterNetTopo(config_file)
    tl = network_topo.get_timeline()
    node0 = network_topo.get_nodes_by_type("QuantumRouter")[0]
    node1 = network_topo.get_nodes_by_type("QuantumRouter")[1]
    node0_memory = node0.components[node0.memo_arr_name][0]
    node1_memory = node1.components[node1.memo_arr_name][0]

    # step 2: get the density matrix from QuantumSavory
    etaA = 0.5
    etaB = 0.5
    Pd   = 0
    etaD = 0.85
    V    = 0.9
    m    = 0
    rho = get_density_matrix_from_qsavory(etaA, etaB, Pd, etaD, V, m)
    print(f"Density matrix from StatesZoo: {rho}")

    # step 3: entangle two memories in the network with the density matrix
    entangle_memory(tl, node0_memory, node1_memory, rho)
    key0 = node0_memory.qstate_key
    print(f"Memory 0 state:\n{tl.quantum_manager.get(key0)}\n")
    key1 = node1_memory.qstate_key
    print(f"Memory 1 state:\n{tl.quantum_manager.get(key1)}\n")


if __name__ == "__main__":
    # stateszoo()
    stateszoo2sequence()
