from NEQR import neqr_encoding
from QFT import qft_to_position_qubits,inverse_qft_to_position_qubits
from Filter import add_ideal_filter_oracle
from matplotlib import pyplot as plt
from simulation_testing import analyze_filter_results, visualize_quantum_images
from IBM_Hardware_testing import setup_ibm_quantum, run_on_ibm_hardware, analyze_ibm_results

# Parameters

IMAGE_SIZE = 2  # 2x2 image
D0 = 0.2 * IMAGE_SIZE  # D0 = 0.4
FILTER_TYPE = "high_pass"  # Change to "low_pass"
position_qubits = [8, 9]
ancilla_qubit = 10
ibm_hardware_test = "no"
# Circuit creation
qc = neqr_encoding()
qft_to_position_qubits(qc)
add_ideal_filter_oracle(qc, position_qubits, ancilla_qubit, FILTER_TYPE, D0)
inverse_qft_to_position_qubits(qc)
qc.measure(range(11), range(11))

# Depth and size
print('Circuit depth: ', qc.decompose().depth())
print('Circuit size: ', qc.decompose().size())

# Draw the circuit
fig = qc.draw(output='mpl', style='iqp', scale=0.75, fold=-1)
plt.title('NEQR + Ideal Filter Circuit')
plt.tight_layout()
plt.show()

# Run simulation and visualize results
if ibm_hardware_test == "yes":
    # IBM Hardware execution
    print("Setting up IBM quantum hardware...")
    service, backend = setup_ibm_quantum()
    print(f"Using backend: {backend.name}")

    result = run_on_ibm_hardware(qc, backend, shots=1024)

    if result:
        filtered_results, unfiltered_results = analyze_ibm_results(result)
        visualize_quantum_images(filtered_results, unfiltered_results)
    else:
        print("IBM hardware execution failed!")
else:
    # Local simulation (default)
    print("Running local simulation...")
    filtered_results, unfiltered_results = analyze_filter_results(qc)
    visualize_quantum_images(filtered_results, unfiltered_results)