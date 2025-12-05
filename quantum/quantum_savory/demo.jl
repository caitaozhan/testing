using QuantumSavory
using ResumableFunctions
using ConcurrentSim

sim = Simulation()
regA = Register(1) # alice
regB = Register(2) # bob

# entangle Alice's and Bob's first qubit
bell_state = (Z1 ⊗ Z1 + Z2 ⊗ Z2) / sqrt(2.0)
initialize!((regA[1], regB[1]), bell_state)

# channel with delay
qc = QuantumChannel(sim, 15.0)

# Alice wants to send "10"
@resumable function alice(env, qc)
    println("Alice: Encoding 10 at $(now(env))")
    apply!(regA[1], Z)
    put!(qc, regA[1])
end

# Bob receives the qubit and decodes it
@resumable function bob(env, qc)
    @yield take!(qc, regB[2]) # wait for the qubit from Alice
    apply!((regB[2], regB[1]), CNOT)
    apply!(regB[2], H)

    bit1 = project_traceout!(regB, 2, Z) - 1
    bit2 = project_traceout!(regB, 1, Z) - 1
    println("Bob decoded the bits at $(now(env)): ", bit1, bit2)
end

@process alice(sim, qc)
@process bob(sim, qc)
run(sim)

