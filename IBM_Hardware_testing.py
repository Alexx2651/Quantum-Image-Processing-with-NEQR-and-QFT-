#!/usr/bin/env python3

from simulation_testing import visualize_quantum_images

import time
from qiskit import transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2


def setup_ibm_quantum():
    service = QiskitRuntimeService()
    backend = service.least_busy(
        simulator=False,
        operational=True,
        min_num_qubits=11
    )
    return service, backend


def run_on_ibm_hardware(circuit, backend, shots=1024):
    qc_no_measure = circuit.copy()
    qc_no_measure.remove_final_measurements()
    transpiled_qc = transpile(qc_no_measure, backend=backend, optimization_level=3)
    transpiled_qc.measure_all()

    sampler = SamplerV2(mode=backend)
    job = sampler.run([transpiled_qc], shots=shots)

    print(f"Job ID: {job.job_id()}")
    print("Job submitted. Waiting for results...")

    start_time = time.time()
    status = job.status()
    status_name = status if isinstance(status, str) else status.name

    while status_name not in ['DONE', 'ERROR', 'CANCELLED']:
        elapsed = time.time() - start_time
        print(f"Status: {status_name} (elapsed: {elapsed:.0f}s)")
        time.sleep(30)

        status = job.status()
        status_name = status if isinstance(status, str) else status.name

    if status_name == 'DONE':
        result = job.result()
        return result
    else:
        return None


def analyze_ibm_results(result):
    pub_result = result[0]

    counts = None
    if hasattr(pub_result, 'data'):
        data = pub_result.data
        if hasattr(data, 'cr'):
            counts = data.cr.get_counts()
        elif hasattr(data, 'c'):
            counts = data.c.get_counts()
        elif hasattr(data, 'meas'):
            counts = data.meas.get_counts()

    if counts is None and hasattr(pub_result, 'get_counts'):
        counts = pub_result.get_counts()

    filtered_results = {}
    unfiltered_results = {}

    for bitstring, count in counts.items():
        ancilla_bit = bitstring[0]
        intensity_bits = bitstring[3:11]
        position_bits = bitstring[1:3]

        key = f"pos_{position_bits}_int_{intensity_bits}"

        if ancilla_bit == '1':
            filtered_results[key] = filtered_results.get(key, 0) + count
        else:
            unfiltered_results[key] = unfiltered_results.get(key, 0) + count

    return filtered_results, unfiltered_results