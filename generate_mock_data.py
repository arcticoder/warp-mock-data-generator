#!/usr/bin/env python3
"""
Reads quantum-geometry signatures and an instrument specification,
synthesizes mock time-series signals (sine carriers + Gaussian envelope + white noise),
and writes NDJSON and AsciiMath summary outputs.
"""

import argparse
import json
import ast
import ndjson
import numpy as np

def parse_key_value_am(path):
    """Parse a simple 'Key: Value' AsciiMath file into a dict."""
    meta = {}
    with open(path, 'r') as f:
        for line in f:
            if ':' not in line:
                continue
            key, val = line.split(':', 1)
            key = key.strip()
            val = val.strip()
            # Try to interpret Python literals (lists, numbers)
            try:
                meta[key] = ast.literal_eval(val)
            except Exception:
                meta[key] = val
    return meta

def load_signatures(path_ndjson, path_am):
    """Load signature list and metadata."""
    with open(path_ndjson) as f:
        sigs = ndjson.load(f)
    meta = parse_key_value_am(path_am)
    return sigs, meta

def synthesize_signal(freq, width, amp, sampling_rate, duration=1.0):
    """
    Create a time-series:
      amp * sin(2π f t) * Gaussian(t; σ=width) + white noise floor
    """
    t = np.arange(0, duration, 1.0/sampling_rate)
    carrier = amp * np.sin(2 * np.pi * freq * t)
    # Gaussian envelope centered at duration/2
    std = width if width > 0 else duration/8
    env = np.exp(-0.5 * ((t - duration/2)/(std))**2)
    signal = carrier * env
    # Add white noise at 5% of peak amplitude
    noise = 0.05 * amp * np.random.randn(len(t))
    return t, signal + noise

def main():
    p = argparse.ArgumentParser(description="Generate mock detector data from signatures.")
    p.add_argument('--signatures',       required=True, help="signatures.ndjson")
    p.add_argument('--signature-meta',   required=True, help="signatures.am")
    p.add_argument('--instrument-spec',  required=True, help="instrument_spec.am")
    p.add_argument('--output-ndjson',    required=True, help="mock_data.ndjson")
    p.add_argument('--output-meta',      required=True, help="mock_data.am")
    args = p.parse_args()

    # Load inputs
    sigs, sig_meta = load_signatures(args.signatures, args.signature_meta)
    inst = parse_key_value_am(args.instrument_spec)

    sr = int(inst.get('SamplingRate', 4096))
    duration = inst.get('Duration', 1.0)  # allow override in spec

    # Prepare output NDJSON
    out_nd = []
    for sig in sigs:
        label = sig.get('label') or f"{sig_meta.get('TheoryVariant','sig')}_{sigs.index(sig)+1}"
        freq      = float(sig.get('frequency', 0.0))
        width     = float(sig.get('width', duration/8))
        amplitude = float(sig.get('amplitude', 1.0))

        t, ts = synthesize_signal(freq, width, amplitude, sr, duration)
        out_nd.append({
            "label": label,
            "sampling_rate": sr,
            "time_series": ts.tolist()
        })    # Write mock_data.ndjson
    with open(args.output_ndjson, 'w') as f:
        writer = ndjson.writer(f)
        for row in out_nd:
            writer.writerow(row)

    # Write a simple AsciiMath summary
    injection_count = len(out_nd)
    with open(args.output_meta, 'w') as f:
        f.write('[ ')
        f.write(f'InstrumentType = {inst.get("InstrumentType")}, ')
        f.write(f'SamplingRate = {sr}, ')
        f.write(f'NoiseModel = {inst.get("NoiseModel")}, ')
        f.write(f'InjectionCount = {injection_count} ')
        f.write(']\n')

    print(f"Wrote {injection_count} mock signals to {args.output_ndjson}")
    print(f"Wrote summary to {args.output_meta}")

if __name__ == '__main__':
    main()