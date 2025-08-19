def add_ideal_filter_oracle(circuit, position_qubits, ancilla_qubit, filter_type="low_pass", D0=0.4):
    circuit.barrier()

    if filter_type == "low_pass":
        # Flip ancilla when position = (0,0) -> both qubits are 0
        circuit.x(position_qubits[0])  # NOT qubit 8
        circuit.x(position_qubits[1])  # NOT qubit 9
        circuit.ccx(position_qubits[0], position_qubits[1], ancilla_qubit)  # CCX when both are 0
        circuit.x(position_qubits[0])  # Restore qubit 8
        circuit.x(position_qubits[1])  # Restore qubit 9

    elif filter_type == "high_pass":
        # Flip ancilla when position ≠ (0,0) -> NOT(both qubits are 0)
        circuit.x(ancilla_qubit)  # Start with ancilla = 1
        circuit.x(position_qubits[0])  # NOT qubit 8
        circuit.x(position_qubits[1])  # NOT qubit 9
        circuit.ccx(position_qubits[0], position_qubits[1], ancilla_qubit)  # Flip back to 0 when both are 0
        circuit.x(position_qubits[0])  # Restore qubit 8
        circuit.x(position_qubits[1])  # Restore qubit 9

    circuit.barrier()
