from NEQR import neqr_encoding
from matplotlib import pyplot as plt
from qiskit_aer import Aer
from qiskit import transpile
import numpy as np


def dict_to_image(data):
    image = np.zeros((2, 2), dtype=np.uint8)

    for bitstring, count in data.items():
        # Ignore first bit

        pos_bits = bitstring[1:3]
        gray_bits = bitstring[3:]

        # Convert position bits to row,col
        row = int(pos_bits[0], 2)
        col = int(pos_bits[1], 2)

        # Convert 8-bit gray value
        gray_val = int(gray_bits, 2)

        # Use the value with the largest count if multiple entries map to same pixel
        if image[row, col] == 0 or count > 0:
            image[row, col] = gray_val

    # Original image
    plt.imshow(image, cmap='gray', vmin=0, vmax=255, interpolation='nearest')

    for i in range(2):
        for j in range(2):
            plt.text(j, i, f'{int(image[i, j])}',
                     ha='center', va='center', color='red', fontsize=12, fontweight='bold')

    return image


def show_image(image):
    plt.imshow(image, cmap="gray", vmin=0, vmax=255)
    plt.axis("off")
    plt.show()


def create_negative_image(qc):
    (intensity, position, ancilla) = qc.qregs
    (q0, q1, q2, q3, q4, q5, q6, q7) = intensity

    qc.x(q0)
    qc.x(q1)
    qc.x(q2)
    qc.x(q3)
    qc.x(q4)
    qc.x(q5)
    qc.x(q6)
    qc.x(q7)

    return qc


qc_neg = neqr_encoding()
qc_neg.barrier()
qc_neg = create_negative_image(qc_neg)

qc_neg.barrier()
qc_neg.measure([0,1,2,3,4,5,6, 7, 8,9,10], [0,1,2,3,4,5,6, 7, 8,9,10])
qc_neg.draw(output='mpl', style='iqp', scale=0.75, fold=-1)
plt.title('NEQR + Negative')
plt.tight_layout()
plt.show()

simulator = Aer.get_backend('aer_simulator')
compiled_circuit = transpile(qc_neg, simulator)
job = simulator.run(compiled_circuit, shots=8192)
result = job.result()
counts = result.get_counts(compiled_circuit)
print('Rezultatele masuratorii: ',counts)
img = dict_to_image(counts)
print('Matricea imaginii: \n', img)  # prints the 2x2 grayscale values
show_image(img)