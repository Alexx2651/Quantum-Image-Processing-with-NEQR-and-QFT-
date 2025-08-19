from matplotlib import pyplot as plt
from qiskit_aer import Aer
import numpy as np

# Import functions from local modules
from NEQR import neqr_encoding
from QFT import qft_to_position_qubits, inverse_qft_to_position_qubits


def add_ideal_filter_oracle(circuit, position_qubits, ancilla_qubit, filter_type="low_pass", D0=0.4):
    """
    Add ideal frequency filter oracle based on AECE study methodology.

    Args:
        circuit: Quantum circuit
        position_qubits: Position qubits indices [qubit8, qubit9]
        ancilla_qubit: Filter ancilla qubit index
        filter_type: "high_pass" or "low_pass"
        D0: Frequency threshold
    """
    circuit.barrier()

    if filter_type == "low_pass":
        # Low-pass: S_good = {(k,p) | D(k,p) ≤ D0}
        # Flip ancilla when position = (0,0)
        circuit.x(position_qubits[0])
        circuit.x(position_qubits[1])
        circuit.ccx(position_qubits[0], position_qubits[1], ancilla_qubit)
        circuit.x(position_qubits[0])
        circuit.x(position_qubits[1])

    elif filter_type == "high_pass":
        # High-pass: S_good = {(k,p) | D(k,p) ≥ D0}
        # Flip ancilla when position ≠ (0,0)
        circuit.x(ancilla_qubit)
        circuit.x(position_qubits[0])
        circuit.x(position_qubits[1])
        circuit.ccx(position_qubits[0], position_qubits[1], ancilla_qubit)
        circuit.x(position_qubits[0])
        circuit.x(position_qubits[1])

    circuit.barrier()


def create_neqr_image_with_ideal_filter(filter_type="high_pass", image_size=2):
    """
    Create NEQR quantum image processing circuit with ideal frequency filter.

    Args:
        filter_type: "high_pass" or "low_pass"
        image_size: Size of the square image (default: 2 for 2x2)

    Returns:
        QuantumCircuit: Complete filtering circuit
    """
    # Initialize quantum circuit with NEQR encoding
    qc = neqr_encoding()

    # Define circuit parameters
    position_qubits = [8, 9]
    ancilla_qubit = 10
    D0 = 0.2 * image_size

    # Apply QFT to position qubits
    qft_to_position_qubits(qc, position_qubits)

    # Apply ideal filter oracle
    add_ideal_filter_oracle(qc, position_qubits, ancilla_qubit, filter_type, D0)

    # Apply inverse QFT to position qubits
    inverse_qft_to_position_qubits(qc, position_qubits)

    # Add measurements
    qc.measure(range(11), range(11))

    return qc


def main():
    """Main function to create and visualize the quantum filtering circuit."""
    # Create the filtering circuit
    qc_filtered = create_neqr_image_with_ideal_filter(filter_type="high_pass", image_size=2)

    # Circuit statistics
    depth = qc_filtered.decompose().depth()
    size = qc_filtered.decompose().size()

    print(f"Circuit depth: {depth}")
    print(f"Circuit size: {size}")

    # Visualize circuit
    fig = qc_filtered.draw(output='mpl', style='iqp', scale=0.75, fold=-1)
    plt.title('NEQR Quantum Image Filtering Circuit')
    plt.tight_layout()
    plt.show()

    return qc_filtered


if __name__ == "__main__":
    qc_filtered = main()