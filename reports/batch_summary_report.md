# Batch Integrity Evaluation Summary

**Total Submissions Evaluated:** 15

## 1. Risk Distribution Overview

| Risk Classification | Count | Percentage |
| :--- | :---: | :---: |
| 🔴 **HIGH RISK** | 3 | 20.0% |
| 🟡 **MEDIUM RISK** | 2 | 13.3% |
| 🟢 **LOW RISK (Passed)** | 7 | 46.7% |
| ⚠️ **FLAGGED / DEGRADED** | 3 | 20.0% |


## 2. Submission Results Table

| Document ID | Risk Category | Peer % | External % | AI Prob % | Status |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `submission_01_original_fintech.pdf` | 🟡 MEDIUM | 33.3% | 0.0% | 15.0% | `SUCCESS` |
| `submission_02_video_pitch.mp4` | 🔴 HIGH | 100.0% | 0.0% | 26.4% | `SUCCESS` |
| `submission_03_logistics_strategy.docx` | 🔴 HIGH | 50.0% | 50.0% | 28.5% | `SUCCESS` |
| `submission_04_logistics_rewritten.docx` | 🔴 HIGH | 50.0% | 0.0% | 72.8% | `SUCCESS` |
| `submission_05_corrupt_empty.pdf` | ⚠️ FLAGGED | 0.0% | 0.0% | 0.0% | `SKIPPED_EMPTY` |
| `submission_06_silent_video.mp4` | ⚠️ FLAGGED | 0.0% | 0.0% | 0.0% | `SKIPPED_SILENT` |
| `submission_07_corrupted.docx` | ⚠️ FLAGGED | 0.0% | 0.0% | 0.0% | `SKIPPED_CORRUPT` |
| `submission_08_ev_bus_depot_analysis.pdf` | 🟢 LOW | 0.0% | 0.0% | 14.8% | `SUCCESS` |
| `submission_09_ev_battery_lifecycle.docx` | 🟢 LOW | 0.0% | 0.0% | 14.3% | `SUCCESS` |
| `submission_10_ev_municipal_finance.pdf` | 🟢 LOW | 0.0% | 0.0% | 13.4% | `SUCCESS` |
| `submission_11_ev_route_telemetry.docx` | 🟢 LOW | 0.0% | 0.0% | 13.6% | `SUCCESS` |
| `submission_12_ev_grid_load_balancing.pdf` | 🟢 LOW | 0.0% | 0.0% | 12.9% | `SUCCESS` |
| `submission_13_ai_generated_essay.docx` | 🟢 LOW | 0.0% | 0.0% | 23.0% | `SUCCESS` |
| `submission_14_external_plagiarism.pdf` | 🟡 MEDIUM | 0.0% | 33.3% | 16.4% | `SUCCESS` |
| `submission_15_genuine_original.pdf` | 🟢 LOW | 0.0% | 0.0% | 15.0% | `SUCCESS` |


## 3. Pairwise Cross-Document Similarity Matrix

*Values represent max semantic overlap between document chunk vectors (excluding self-matches).*

> **Legend:** **D1**: `submission_01_original_fintech.pdf`, **D2**: `submission_02_video_pitch.mp4`, **D3**: `submission_03_logistics_strategy.docx`, **D4**: `submission_04_logistics_rewritten.docx`, **D5**: `submission_05_corrupt_empty.pdf`, **D6**: `submission_06_silent_video.mp4`, **D7**: `submission_07_corrupted.docx`, **D8**: `submission_08_ev_bus_depot_analysis.pdf`, **D9**: `submission_09_ev_battery_lifecycle.docx`, **D10**: `submission_10_ev_municipal_finance.pdf`, **D11**: `submission_11_ev_route_telemetry.docx`, **D12**: `submission_12_ev_grid_load_balancing.pdf`, **D13**: `submission_13_ai_generated_essay.docx`, **D14**: `submission_14_external_plagiarism.pdf`, **D15**: `submission_15_genuine_original.pdf`

| Doc | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | D10 | D11 | D12 | D13 | D14 | D15 |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **D1** | — | **`0.97`** 🔴 | 0.18 | 0.11 | 0.00 | 0.00 | 0.00 | 0.24 | 0.07 | 0.27 | 0.14 | 0.11 | 0.32 | 0.13 | 0.03 |
| **D2** | **`0.97`** 🔴 | — | 0.12 | 0.07 | 0.00 | 0.00 | 0.00 | 0.22 | 0.05 | 0.23 | 0.12 | 0.11 | 0.22 | 0.08 | -0.01 |
| **D3** | 0.18 | 0.12 | — | **`0.87`** 🔴 | 0.00 | 0.00 | 0.00 | 0.11 | 0.46 | 0.16 | 0.24 | 0.23 | 0.09 | 0.33 | 0.11 |
| **D4** | 0.11 | 0.07 | **`0.87`** 🔴 | — | 0.00 | 0.00 | 0.00 | 0.12 | 0.48 | 0.12 | 0.23 | 0.17 | 0.05 | 0.30 | 0.07 |
| **D5** | 0.00 | 0.00 | 0.00 | 0.00 | — | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| **D6** | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | — | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| **D7** | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | — | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| **D8** | 0.24 | 0.22 | 0.11 | 0.12 | 0.00 | 0.00 | 0.00 | — | 0.36 | 0.49 | 0.32 | 0.49 | 0.06 | 0.18 | -0.04 |
| **D9** | 0.07 | 0.05 | 0.46 | 0.48 | 0.00 | 0.00 | 0.00 | 0.36 | — | 0.36 | 0.25 | 0.33 | 0.05 | 0.19 | 0.00 |
| **D10** | 0.27 | 0.23 | 0.16 | 0.12 | 0.00 | 0.00 | 0.00 | 0.49 | 0.36 | — | 0.40 | 0.32 | 0.15 | 0.23 | 0.00 |
| **D11** | 0.14 | 0.12 | 0.24 | 0.23 | 0.00 | 0.00 | 0.00 | 0.32 | 0.25 | 0.40 | — | 0.21 | 0.11 | 0.05 | -0.01 |
| **D12** | 0.11 | 0.11 | 0.23 | 0.17 | 0.00 | 0.00 | 0.00 | 0.49 | 0.33 | 0.32 | 0.21 | — | 0.08 | 0.22 | -0.05 |
| **D13** | 0.32 | 0.22 | 0.09 | 0.05 | 0.00 | 0.00 | 0.00 | 0.06 | 0.05 | 0.15 | 0.11 | 0.08 | — | 0.33 | 0.03 |
| **D14** | 0.13 | 0.08 | 0.33 | 0.30 | 0.00 | 0.00 | 0.00 | 0.18 | 0.19 | 0.23 | 0.05 | 0.22 | 0.33 | — | 0.09 |
| **D15** | 0.03 | -0.01 | 0.11 | 0.07 | 0.00 | 0.00 | 0.00 | -0.04 | 0.00 | 0.00 | -0.01 | -0.05 | 0.03 | 0.09 | — |

