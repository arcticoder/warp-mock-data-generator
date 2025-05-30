# warp-mock-data-generator

Generate synthetic observational datasets from quantum-geometry signatures for LIGO, EHT, and similar instruments.

## Description

This repository provides a script, `generate_mock_data.py`, which takes:

1. **Quantum-geometry signatures**  
   - `signatures.ndjson`: one JSON-line per signature:
```json
{ "label": "...", "frequency": <Hz>, "width": <s>, "amplitude": <strain> }
```
   - `signatures.am`: simple AsciiMath metadata (e.g. theory variant, number of signatures).

2. **Instrument specification**  
   - `instrument_spec.am`: key-value pairs describing the detector:
```
InstrumentType: GravitationalWaveDetector
FrequencyRange: [10, 10000] Hz
Sensitivity: 1e-23 m/sqrt(Hz)
SamplingRate: 16384 Hz
BandwidthLimits: [10, 7000] Hz
NoiseModel: AdvancedLIGO
```

It synthesizes mock detector outputs (noisy sine-wave injections) and writes:

- `mock_data.ndjson`: one JSON-line per signal:
```json
  {
    "label": "...",
    "sampling_rate": 16384,
    "time_series": [0.0, 1.2e-24, 2.3e-24, …]
  }
```

-   `mock_data.am`: AsciiMath summary of detector and injection settings.
    

## Requirements

-   Python 3.8+
    
-   `numpy`
    
-   `scipy`
    
-   `ndjson`
    

Install dependencies:

```bash
pip install numpy scipy ndjson
```

## Usage

```bash
python generate_mock_data.py `
  --signatures signatures.ndjson `
  --signature-meta signatures.am `
  --instrument-spec instrument_spec.am `
  --output-ndjson mock_data.ndjson `
  --output-meta mock_data.am
```

## Example

After running, a line from `mock_data.ndjson` might be:

```json
{
  "label": "warp-curvature_mode1",
  "sampling_rate": 16384,
  "time_series": [0.0, 1.2e-23, 2.4e-23, …]
}
```

And `mock_data.am` could contain:

```ini
[ InstrumentType = GravitationalWaveDetector,
  SamplingRate = 16384,
  NoiseModel = AdvancedLIGO,
  InjectionCount = 2 ]
```