from numpy import pi

def qft_rotations(circuit, n):
    """Performs qft on the first n qubits in circuit (without swaps)"""
    if n == 0:
        return circuit
    n -= 1
    circuit.h(n)
    for qubit in range(n):
        circuit.cp(pi/2**(n-qubit), qubit, n)
    # At the end of our function, we call the same function again on
    # the next qubits (we reduced n by one earlier in the function)
    qft_rotations(circuit, n)

def swap_registers(circuit, n):
    for qubit in range(n//2):
        circuit.swap(qubit, n-qubit-1)
    return circuit

def qft(circuit, n):
    """QFT on the first n qubits in circuit"""
    qft_rotations(circuit, n)
    swap_registers(circuit, n)
    return circuit
def qft_inverse(circuit, n):
    """Inverse QFT on the first n qubits"""
    # Reverse the QFT operations
    swap_registers(circuit, n)
    qft_rotations_inverse(circuit, n)
    return circuit


def qft_rotations_inverse(circuit, n):
    """Inverse QFT rotations"""
    if n == 0:
        return circuit

    # Apply inverse rotations in reverse order
    for qubit in range(n - 1):
        circuit.cp(-pi / 2 ** (n - 1 - qubit), qubit, n - 1)
    circuit.h(n - 1)

    # Recursively apply to remaining qubits
    qft_rotations_inverse(circuit, n - 1)