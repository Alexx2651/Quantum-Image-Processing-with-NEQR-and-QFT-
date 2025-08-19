#!/usr/bin/env python3
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit


def neqr_encoding(pixel_values=None):
    # Default pixel values if not provided
    if pixel_values is None:
        pixel_values = {
            '00': '00000000',  # 0
            '01': '01100100',  # 100
            '10': '11001000',  # 200
            '11': '11111111'   # 255
        }

    # Initialize quantum registers
    intensity = QuantumRegister(8, 'intensity')  # 8-bit intensity
    position = QuantumRegister(2, 'position')  # 2-bit position
    ancilla = QuantumRegister(1, 'ancilla')  # Filter ancilla
    cr = ClassicalRegister(11, 'cr')  # Classical register

    # Create quantum circuit
    qc = QuantumCircuit(intensity, position, ancilla, cr)

    # Initialize intensity qubits (optional identity gates)
    for i in range(8):
        qc.id(i)

    # Create superposition for pixel positions
    qc.h(8)  # position qubit 0
    qc.h(9)  # position qubit 1
    qc.barrier()

    # Encode pixel 00 (value = pixel_values['00'])
    # Since qubits start in |0⟩ state and value00 is '00000000', use identity gates
    for i in range(8):
        qc.id(i)  # Identity gates for position 00 (value = 0)
    qc.barrier()

    # Encode pixel 01 (value = pixel_values['01'])
    value01 = pixel_values['01']
    qc.x(9)  # Set position to 01
    for i, bit in enumerate(value01[::-1]):  # Reverse order
        if bit == '1':
            qc.ccx(9, 8, i)  # Controlled on position = 01
    qc.x(9)  # Reset position
    qc.barrier()

    # Encode pixel 10 (value = pixel_values['10'])
    value10 = pixel_values['10']
    qc.x(8)  # Set position to 10
    for i, bit in enumerate(value10[::-1]):
        if bit == '1':
            qc.ccx(9, 8, i)  # Controlled on position = 10
    qc.x(8)  # Reset position
    qc.barrier()

    # Encode pixel 11 (value = pixel_values['11'])
    value11 = pixel_values['11']
    for i, bit in enumerate(value11[::-1]):
        if bit == '1':
            qc.ccx(8, 9, i)  # Controlled on position = 11
    qc.barrier()

    return qc
