from matplotlib import pyplot as plt
from qiskit_aer import Aer
from qiskit import transpile
import numpy as np

# Import functions from local modules
from Filter import create_neqr_image_with_filter


def analyze_filter_results(qc, shots=8192):
    """Run circuit and analyze filtering results"""
    simulator = Aer.get_backend('aer_simulator')
    compiled_circuit = transpile(qc, simulator)
    job = simulator.run(compiled_circuit, shots=shots)
    result = job.result()
    counts = result.get_counts(compiled_circuit)

    # Analyze results by ancilla bit
    filtered_results = {}
    unfiltered_results = {}

    for bitstring, count in counts.items():
        ancilla_bit = bitstring[0]  # First bit is ancilla (rightmost in circuit)
        intensity_bits = bitstring[3:11]  # Bits 3-10 are intensity
        position_bits = bitstring[1:3]  # Bits 1-2 are position

        if ancilla_bit == '1':
            key = f"pos_{position_bits}_int_{intensity_bits}"
            filtered_results[key] = filtered_results.get(key, 0) + count
        else:
            key = f"pos_{position_bits}_int_{intensity_bits}"
            unfiltered_results[key] = unfiltered_results.get(key, 0) + count

    return filtered_results, unfiltered_results


def visualize_quantum_images(filtered_results, unfiltered_results):
    """Create simple 2x2 image visualization of quantum filter results"""
    # Initialize 2x2 images
    filtered_image = np.zeros((2, 2), dtype=float)
    unfiltered_image = np.zeros((2, 2), dtype=float)

    # Process filtered results
    total_filtered_shots = sum(filtered_results.values())
    for key, count in filtered_results.items():
        parts = key.split('_')
        pos_bits = parts[1]
        int_bits = parts[3]
        row = int(pos_bits[0])
        col = int(pos_bits[1])
        intensity = int(int_bits, 2)
        if total_filtered_shots > 0:
            filtered_image[row, col] += intensity * (count / total_filtered_shots)

    # Process unfiltered results
    total_unfiltered_shots = sum(unfiltered_results.values())
    for key, count in unfiltered_results.items():
        parts = key.split('_')
        pos_bits = parts[1]
        int_bits = parts[3]
        row = int(pos_bits[0])
        col = int(pos_bits[1])
        intensity = int(int_bits, 2)
        if total_unfiltered_shots > 0:
            unfiltered_image[row, col] += intensity * (count / total_unfiltered_shots)

    # Original image for reference
    original_image = np.array([[0, 100], [200, 255]], dtype=float)

    # Create visualization
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))

    # Original image
    axes[0].imshow(original_image, cmap='gray', vmin=0, vmax=255, interpolation='nearest')
    axes[0].set_title('Original NEQR Image\n(2x2 pixels)')
    axes[0].set_xlabel('Pixel values: 0, 100, 200, 255')
    for i in range(2):
        for j in range(2):
            axes[0].text(j, i, f'{int(original_image[i, j])}',
                         ha='center', va='center', color='red', fontsize=12, fontweight='bold')

    # Filtered component
    axes[1].imshow(filtered_image, cmap='gray', vmin=0, vmax=255, interpolation='nearest')
    axes[1].set_title('Filtered Component\n(Ancilla = 1)')
    axes[1].set_xlabel(f'Total measurements: {total_filtered_shots}')
    for i in range(2):
        for j in range(2):
            axes[1].text(j, i, f'{int(filtered_image[i, j])}',
                         ha='center', va='center', color='red', fontsize=12, fontweight='bold')

    # Unfiltered component
    axes[2].imshow(unfiltered_image, cmap='gray', vmin=0, vmax=255, interpolation='nearest')
    axes[2].set_title('Unfiltered Component\n(Ancilla = 0)')
    axes[2].set_xlabel(f'Total measurements: {total_unfiltered_shots}')
    for i in range(2):
        for j in range(2):
            axes[2].text(j, i, f'{int(unfiltered_image[i, j])}',
                         ha='center', va='center', color='red', fontsize=12, fontweight='bold')

    # Clean layout
    for ax in axes:
        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(['Col 0', 'Col 1'])
        ax.set_yticklabels(['Row 0', 'Row 1'])

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    qc_filtered = create_neqr_image_with_filter()
    filtered, unfiltered = analyze_filter_results(qc_filtered)
    visualize_quantum_images(filtered, unfiltered)