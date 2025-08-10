from matplotlib import pyplot as plt
from qiskit.visualization import plot_bloch_multivector
from qiskit_aer import Aer

# Import functions from local modules
from NEQR import neqr_encoding
from QFT import qft, qft_inverse


def add_quantum_oracle(circuit, intensity_qubits, position_qubits, ancilla_qubit, filter_type="low_pass"):
    """
    Add quantum oracle for frequency domain filtering

    Args:
        circuit: Quantum circuit
        intensity_qubits: Range of intensity qubits (0-7)
        position_qubits: Position qubits [qubit8, qubit9]
        ancilla_qubit: Filter ancilla qubit
        filter_type: "high_pass" or "low_pass"
    """
    circuit.barrier()

    if filter_type == "low_pass":
        # Low-pass: Keep only DC component (00)
        # Flip ancilla when both position qubits are 0
        # Use X gates to create NOT logic, then controlled operation
        circuit.x(position_qubits[0])  # NOT gate
        circuit.x(position_qubits[1])  # NOT gate
        circuit.ccx(position_qubits[0], position_qubits[1], ancilla_qubit)  # CCX when both are 0
        circuit.x(position_qubits[0])  # Restore
        circuit.x(position_qubits[1])  # Restore

    elif filter_type == "high_pass":
        # High-pass: Keep AC components (01, 10, 11) - everything except 00
        # Flip ancilla when NOT (both position qubits are 0)
        circuit.x(ancilla_qubit)  # Start with ancilla = 1
        circuit.x(position_qubits[0])  # NOT gate
        circuit.x(position_qubits[1])  # NOT gate
        circuit.ccx(position_qubits[0], position_qubits[1], ancilla_qubit)  # Flip back to 0 when both pos are 0
        circuit.x(position_qubits[0])  # Restore
        circuit.x(position_qubits[1])  # Restore

    circuit.barrier()


def create_neqr_image_with_filter():
    """Create NEQR quantum image with frequency domain filtering"""

    print("=== QUANTUM IMAGE FILTERING CIRCUIT ===")

    # Create the quantum circuit using NEQR encoding
    qc = neqr_encoding()

    print(f"Total qubits: {qc.num_qubits}")
    print(f"Intensity qubits: {list(range(8))}")
    print(f"Position qubits: {list(range(8, 10))}")
    print(f"Ancilla qubit: {10}")

    # === STEP 3: APPLY QFT ===
    print("Building circuit: Applying QFT...")
    qft(qc, 8)  # Apply QFT to intensity qubits only
    qc.barrier()
    print("✓ QFT applied to intensity qubits")

    # === STEP 4: APPLY FILTER ORACLE ===
    # You can change this to "low_pass" for low-pass filtering
    FILTER_TYPE = "high_pass"
    print(f"Building circuit: Adding {FILTER_TYPE} filter oracle...")

    add_quantum_oracle(qc, list(range(8)), [8, 9], 10, FILTER_TYPE)
    print(f"✓ {FILTER_TYPE.replace('_', '-').title()} filter oracle applied")

    # === STEP 5: APPLY INVERSE QFT ===
    print("Building circuit: Applying inverse QFT...")
    qft_inverse(qc, 8)  # Apply inverse QFT to intensity qubits
    qc.barrier()
    print("✓ Inverse QFT applied")

    # === STEP 6: MEASUREMENT ===
    print("Building circuit: Adding measurements...")
    qc.measure(range(11), range(11))

    return qc


qc_filtered = create_neqr_image_with_filter()
print('Filtered Circuit dimensions:')
print('Circuit depth: ', qc_filtered.decompose().depth())
print('Circuit size: ', qc_filtered.decompose().size())

# Draw the circuit
fig = qc_filtered.draw(output='mpl', style='iqp', scale=0.75, fold=-1)
plt.title('NEQR + QFT+Filter Circuit')
plt.tight_layout()
plt.show()