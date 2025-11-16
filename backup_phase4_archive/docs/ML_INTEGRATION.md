# Phase 4 – ML Inference

This document outlines how to work with the Phase 4 ML inference shim and associated tooling.

## Artifacts
- Baseline classifier: `models/artifacts/model.pkl`
- Feature scaler: `models/artifacts/scaler.pkl`
- Metadata: `models/artifacts/meta.json`
- Optional sequence model: `models/artifacts/lstm.pt`

## CLI Helpers

```bash
# Run inference against a telemetry log
PYTHONPATH=. .venv/bin/python -m inference.ml_inference <log_id_or_path>

# Smoke test wrapper (non-terminating mode)
python monitor/jail_wrapper.py --no-kill --jail sandbox_jail -- /bin/sleep 1
```

## Programmatic Usage

```python
from inference import ml_inference

result = ml_inference.predict_run("monitor/logs/synth/mal_memory_leak.jsonl")
print(result["label"], result["score"], result["explanation_top"])
```

The returned payload contains:
- `runId`: identifier used to resolve the telemetry file
- `model`: `rf`, `svm`, `lstm`, or `none`
- `score`: highest probability or decision score
- `label`: predicted category (benign/malicious/unknown)
- `probs`: array of `{label, prob}` objects when available
- `explanation_top`: map of the most influential features
- `meta`: snapshot of artifact metadata

Use `predict_sequence(seq)` when working with enriched windowed telemetry for the LSTM path.

## Tests

Run the smoke test to validate inference setup and record results automatically:

```bash
bash tests/test_inference.sh
```

The script prints a JSON response and appends a result line to `phase3/TEST_RUNS.md`. Ensure the virtual environment is activated or prefix commands with `.venv/bin/python` as shown above.

## Inference API (quick reference)

Programmatic usage is provided via `inference.ml_inference.MLInferenceEngine`.

Example:

```python
from inference.ml_inference import MLInferenceEngine
engine = MLInferenceEngine()
result = engine.predict_run("monitor/logs/monitor_run_20251113T031259Z_6962.jsonl")
print(result.to_dict())
```

Returned payload keys of interest: `runId`, `model`, `score`, `label`, `probs`, `explanation_top`, `meta`, `info`.

