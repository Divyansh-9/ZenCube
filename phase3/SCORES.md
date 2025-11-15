# Phase 3 Scores

| Timestamp (UTC) | Item | Score | Notes |
|-----------------|------|-------|-------|
| 2025-11-12T03:58:00Z | File System Restriction (dev-safe) | 1.0 | Implementation complete; chroot flag, dev wrapper, scripts, and regression tests in place |
| 2025-11-12T16:05:00Z | GUI – File Restriction Panel (Python GUI) | 9.0 | Native PySide6 panel with dev-safe workflow, headless test, and documentation updates |
| 2025-11-12T17:22:00Z | Network Restrictions (seccomp + dev-safe) | 9.2 | --no-net flag, Python wrapper logging, GUI toggle, namespace helper, and regression test |
| 2025-11-13T03:17:00Z | Monitoring & Dashboard (Task C) | 9.4 | Sampling monitor, PySide6 dashboard, JSONL artefacts, offscreen regression test, and documentation |
| 2025-11-13T12:48:00Z | Monitoring enhancements (Phase 3) | 9.6 | Matplotlib charts with EWMA, alerts & log rotation, Prometheus exporter, CI workflow, and full regression suite |


| 2025-11-15T12:05:00Z | Phase 4 – Dataset Quality (synthetic + real) | 10.0 | Full dataset scoring (real + synthetic) met diversity/balance targets; `models/train.py` meta.json recorded 61 samples with variance mean 1.05e16 |
| 2025-11-15T12:05:00Z | Phase 4 – Baseline Model (RandomForest) | 9.44 | Final RandomForest training delivered F1_macro 0.84 / accuracy 0.88; artifacts in `models/artifacts/` (model.pkl, scaler.pkl, report.md) |
| 2025-11-15T12:05:00Z | Phase 4 – LSTM Sequence Model | 10.0 | Bidirectional LSTM + run-context features achieved perfect sequence accuracy (score 10.0); `models/artifacts/lstm.pt` saved |

