from matplotlib import pyplot as plt
from qiskit_aer import Aer
import numpy as np

# Import functions from local modules
from NEQR import neqr_encoding
from QFT import qft, qft_inverse


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


def create_neqr_image_with_ideal_filter():
    """Create NEQR quantum image with ideal threshold filter like AECE study"""

    # Create the quantum circuit using NEQR encoding with default pixel values (180, 110)
    qc = neqr_encoding()

    # === APPLY QFT TO POSITION QUBITS ===
    qc.h(9)           # Hadamard on qubit 9 (most significant)
    qc.cp(np.pi/2, 8, 9) # Controlled phase rotation
    qc.h(8)           # Hadamard on qubit 8 (least significant)
    qc.swap(8, 9)     # Swap for correct QFT ordering
    qc.barrier()

    # === APPLY IDEAL FILTER ===
    IMAGE_SIZE = 2  # 2x2 image
    D0 = 0.2 * IMAGE_SIZE  # D0 = 0.4
    FILTER_TYPE = "high_pass"  # Change to "low_pass"

    add_ideal_filter_oracle(qc, [8, 9], 10, FILTER_TYPE, D0)

    # === APPLY INVERSE QFT TO POSITION QUBITS ===
    qc.swap(8, 9)      # Undo the swap first
    qc.h(8)            # Inverse Hadamard on qubit 8
    qc.cp(-np.pi/2, 8, 9) # Inverse controlled phase rotation
    qc.h(9)            # Inverse Hadamard on qubit 9
    qc.barrier()

    # === MEASUREMENT ===
    qc.measure(range(11), range(11))

    return qc


qc_filtered = create_neqr_image_with_ideal_filter()
print('Circuit depth: ', qc_filtered.decompose().depth())
print('Circuit size: ', qc_filtered.decompose().size())

# Draw the circuit
fig = qc_filtered.draw(output='mpl', style='iqp', scale=0.75, fold=-1)
plt.title('NEQR + Ideal Filter Circuit')
plt.tight_layout()
plt.show()