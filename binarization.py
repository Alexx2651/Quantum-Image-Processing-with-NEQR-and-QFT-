from NEQR import neqr_encoding
from matplotlib import pyplot as plt
from qiskit_aer import Aer
from qiskit import transpile
import numpy as np


def apply_binarization(qc):
    """Apply X gates to all intensity qubits (0-7) for binarization"""
    for i in range(8):  # Intensity qubits are 0-7
        qc.x(i)
    qc.barrier()


def run_binarization_simulation(qc, shots=8192):
    """Run simulation and extract pixel values"""
    simulator = Aer.get_backend('aer_simulator')
    compiled_circuit = transpile(qc, simulator)
    job = simulator.run(compiled_circuit, shots=shots)
    result = job.result()
    counts = result.get_counts(compiled_circuit)

    # Extract pixel values for 2x2 image
    binarized_image = np.zeros((2, 2), dtype=float)

    for bitstring, count in counts.items():
        intensity_bits = bitstring[3:11]  # Bits 3-10 are intensity
        position_bits = bitstring[1:3]  # Bits 1-2 are position

        row = int(position_bits[0])
        col = int(position_bits[1])
        intensity = int(intensity_bits, 2)

        binarized_image[row, col] += intensity * (count / shots)

    return binarized_image


def visualize_original_and_binarized(binarized_image):
    """Show original and binarized images side-by-side"""
    # Original image (default NEQR values)
    original_image = np.array([[0, 100], [200, 255]], dtype=float)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    # Original image
    axes[0].imshow(original_image, cmap='gray', vmin=0, vmax=255, interpolation='nearest')
    axes[0].set_title('Original NEQR Image')
    for i in range(2):
        for j in range(2):
            axes[0].text(j, i, f'{int(original_image[i, j])}',
                         ha='center', va='center', color='red', fontsize=12, fontweight='bold')

    # Binarized image
    axes[1].imshow(binarized_image, cmap='gray', vmin=0, vmax=255, interpolation='nearest')
    axes[1].set_title('Binarized Image (X gates applied)')
    for i in range(2):
        for j in range(2):
            axes[1].text(j, i, f'{int(binarized_image[i, j])}',
                         ha='center', va='center', color='red', fontsize=12, fontweight='bold')

    # Clean layout
    for ax in axes:
        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(['Col 0', 'Col 1'])
        ax.set_yticklabels(['Row 0', 'Row 1'])

    plt.tight_layout()
    plt.show()


def main():
    # Step 1: Create NEQR encoded image
    qc = neqr_encoding()

    # Step 2: Apply X gates to all intensity qubits
    apply_binarization(qc)

    # Step 3: Add measurements
    qc.measure(range(11), range(11))

    # Step 4: Show circuit
    print("\nCircuit Statistics:")
    print(f"- Depth: {qc.decompose().depth()}")
    print(f"- Size: {qc.decompose().size()}")

    # Draw the circuit
    fig = qc.draw(output='mpl', style='iqp', scale=0.75, fold=-1)
    plt.title('NEQR + Binarization Circuit')
    plt.tight_layout()
    plt.show()

    # Step 5: Run simulation
    binarized_image = run_binarization_simulation(qc)

    # Step 6: Visualize results
    visualize_original_and_binarized(binarized_image)


if __name__ == "__main__":
    main()