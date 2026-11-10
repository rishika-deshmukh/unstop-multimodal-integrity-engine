# Batch Integrity Evaluation Summary

**Total Submissions Evaluated:** 24

## 1. Risk Distribution Overview

| Risk Classification | Count | Percentage |
| :--- | :---: | :---: |
| 🔴 **HIGH RISK** | 8 | 33.3% |
| 🟡 **MEDIUM RISK** | 2 | 8.3% |
| 🟢 **LOW RISK (Passed)** | 11 | 45.8% |
| ⚠️ **FLAGGED / DEGRADED** | 3 | 12.5% |


## 2. Submission Results Table

| Document ID | Risk Category | Peer % | External % | AI Prob % | Status |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `submission_01_fintech_report.pdf` | 🔴 HIGH | 66.7% | 0.0% | 12.9% | `SUCCESS` |
| `submission_02_video_pitch.mp4` | 🔴 HIGH | 100.0% | 0.0% | 15.7% | `SUCCESS` |
| `submission_03_logistics_strategy.docx` | 🔴 HIGH | 100.0% | 0.0% | 15.0% | `SUCCESS` |
| `submission_04_logistics_rewritten.docx` | 🔴 HIGH | 50.0% | 0.0% | 15.0% | `SUCCESS` |
| `submission_05_logistics_exact_copy.pdf` | 🔴 HIGH | 100.0% | 0.0% | 15.0% | `SUCCESS` |
| `submission_06_corrupt_empty.pdf` | ⚠️ FLAGGED | 0.0% | 0.0% | 0.0% | `SKIPPED_EMPTY` |
| `submission_07_silent_video.mp4` | ⚠️ FLAGGED | 0.0% | 0.0% | 0.0% | `SKIPPED_SILENT` |
| `submission_08_corrupted.docx` | ⚠️ FLAGGED | 0.0% | 0.0% | 0.0% | `SKIPPED_CORRUPT` |
| `submission_09_ev_depot_charging.pdf` | 🟢 LOW | 0.0% | 0.0% | 13.3% | `SUCCESS` |
| `submission_10_ev_battery_degradation.docx` | 🟢 LOW | 0.0% | 0.0% | 12.9% | `SUCCESS` |
| `submission_11_ev_municipal_debt.pdf` | 🟢 LOW | 0.0% | 0.0% | 12.8% | `SUCCESS` |
| `submission_12_ev_route_energy.docx` | 🟢 LOW | 0.0% | 0.0% | 12.5% | `SUCCESS` |
| `submission_13_ev_grid_balancing.pdf` | 🟢 LOW | 0.0% | 0.0% | 11.8% | `SUCCESS` |
| `submission_14_llm_generated_essay.docx` | 🔴 HIGH | 62.5% | 0.0% | 99.6% | `SUCCESS` |
| `submission_15_llm_generated_synthesis.pdf` | 🔴 HIGH | 62.5% | 0.0% | 44.5% | `SUCCESS` |
| `submission_16_quantum_hardware.pdf` | 🟢 LOW | 0.0% | 0.0% | 13.6% | `SUCCESS` |
| `submission_17_quantum_algorithms.docx` | 🟢 LOW | 0.0% | 0.0% | 15.0% | `SUCCESS` |
| `submission_18_external_plagiarism.pdf` | 🔴 HIGH | 0.0% | 50.0% | 14.2% | `SUCCESS` |
| `submission_19_video_paraphrase_pitch.mp4` | 🟡 MEDIUM | 0.0% | 0.0% | 5.0% | `SUCCESS` |
| `submission_20_partially_copied.docx` | 🟡 MEDIUM | 33.3% | 0.0% | 15.1% | `SUCCESS` |
| `submission_21_ev_near_threshold_negative.pdf` | 🟢 LOW | 0.0% | 0.0% | 14.4% | `SUCCESS` |
| `submission_22_wikipedia_urban_transit.pdf` | 🟢 LOW | 0.0% | 0.0% | 29.9% | `SUCCESS` |
| `submission_23_rfc_internet_protocol.docx` | 🟢 LOW | 0.0% | 0.0% | 37.9% | `SUCCESS` |
| `submission_24_wikipedia_renewable_energy.pdf` | 🟢 LOW | 0.0% | 0.0% | 35.2% | `SUCCESS` |


## 3. Pairwise Cross-Document Similarity Matrix

*Values represent max semantic overlap between document chunk vectors (excluding self-matches).*

> **Legend:** **D1**: `submission_01_fintech_report.pdf`, **D2**: `submission_02_video_pitch.mp4`, **D3**: `submission_03_logistics_strategy.docx`, **D4**: `submission_04_logistics_rewritten.docx`, **D5**: `submission_05_logistics_exact_copy.pdf`, **D6**: `submission_06_corrupt_empty.pdf`, **D7**: `submission_07_silent_video.mp4`, **D8**: `submission_08_corrupted.docx`, **D9**: `submission_09_ev_depot_charging.pdf`, **D10**: `submission_10_ev_battery_degradation.docx`, **D11**: `submission_11_ev_municipal_debt.pdf`, **D12**: `submission_12_ev_route_energy.docx`, **D13**: `submission_13_ev_grid_balancing.pdf`, **D14**: `submission_14_llm_generated_essay.docx`, **D15**: `submission_15_llm_generated_synthesis.pdf`, **D16**: `submission_16_quantum_hardware.pdf`, **D17**: `submission_17_quantum_algorithms.docx`, **D18**: `submission_18_external_plagiarism.pdf`, **D19**: `submission_19_video_paraphrase_pitch.mp4`, **D20**: `submission_20_partially_copied.docx`, **D21**: `submission_21_ev_near_threshold_negative.pdf`, **D22**: `submission_22_wikipedia_urban_transit.pdf`, **D23**: `submission_23_rfc_internet_protocol.docx`, **D24**: `submission_24_wikipedia_renewable_energy.pdf`

| Doc | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | D10 | D11 | D12 | D13 | D14 | D15 | D16 | D17 | D18 | D19 | D20 | D21 | D22 | D23 | D24 |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **D1** | — | **`1.00`** 🔴 | 0.18 | 0.12 | 0.18 | 0.00 | 0.00 | 0.00 | 0.21 | 0.08 | 0.32 | 0.22 | 0.12 | 0.36 | 0.24 | 0.06 | 0.07 | 0.09 | `0.67` 🟡 | **`1.00`** 🔴 | 0.25 | 0.23 | 0.13 | -0.01 |
| **D2** | **`1.00`** 🔴 | — | 0.12 | 0.05 | 0.12 | 0.00 | 0.00 | 0.00 | 0.21 | 0.04 | 0.23 | 0.12 | 0.01 | 0.32 | 0.25 | -0.00 | -0.05 | 0.03 | `0.62` 🟡 | 0.59 | 0.12 | 0.16 | 0.06 | -0.01 |
| **D3** | 0.18 | 0.12 | — | **`0.87`** 🔴 | **`1.00`** 🔴 | 0.00 | 0.00 | 0.00 | 0.13 | 0.46 | 0.16 | 0.24 | 0.26 | 0.19 | 0.23 | 0.11 | 0.08 | 0.33 | 0.16 | 0.18 | 0.35 | 0.18 | 0.29 | -0.04 |
| **D4** | 0.12 | 0.05 | **`0.87`** 🔴 | — | **`0.85`** 🔴 | 0.00 | 0.00 | 0.00 | 0.14 | 0.48 | 0.15 | 0.23 | 0.21 | 0.17 | 0.20 | 0.09 | 0.06 | 0.30 | 0.09 | 0.14 | 0.31 | 0.14 | 0.13 | 0.01 |
| **D5** | 0.18 | 0.12 | **`1.00`** 🔴 | **`0.85`** 🔴 | — | 0.00 | 0.00 | 0.00 | 0.15 | 0.45 | 0.15 | 0.24 | 0.25 | 0.21 | 0.25 | 0.10 | 0.08 | 0.34 | 0.16 | 0.19 | 0.34 | 0.18 | 0.29 | -0.05 |
| **D6** | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | — | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| **D7** | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | — | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| **D8** | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | — | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| **D9** | 0.21 | 0.21 | 0.13 | 0.14 | 0.15 | 0.00 | 0.00 | 0.00 | — | 0.30 | 0.46 | 0.36 | 0.41 | 0.54 | 0.59 | 0.01 | -0.04 | 0.14 | 0.00 | 0.21 | 0.44 | 0.29 | 0.09 | 0.11 |
| **D10** | 0.08 | 0.04 | 0.46 | 0.48 | 0.45 | 0.00 | 0.00 | 0.00 | 0.30 | — | 0.40 | 0.25 | 0.34 | 0.52 | 0.43 | 0.03 | -0.02 | 0.19 | -0.05 | 0.08 | 0.59 | 0.25 | 0.10 | 0.12 |
| **D11** | 0.32 | 0.23 | 0.16 | 0.15 | 0.15 | 0.00 | 0.00 | 0.00 | 0.46 | 0.40 | — | 0.41 | 0.28 | 0.59 | `0.61` 🟡 | -0.03 | -0.02 | 0.14 | 0.14 | 0.33 | 0.51 | 0.40 | 0.12 | 0.12 |
| **D12** | 0.22 | 0.12 | 0.24 | 0.23 | 0.24 | 0.00 | 0.00 | 0.00 | 0.36 | 0.25 | 0.41 | — | 0.19 | 0.44 | 0.40 | 0.00 | -0.01 | 0.05 | 0.06 | 0.22 | 0.43 | 0.33 | 0.12 | 0.03 |
| **D13** | 0.12 | 0.01 | 0.26 | 0.21 | 0.25 | 0.00 | 0.00 | 0.00 | 0.41 | 0.34 | 0.28 | 0.19 | — | 0.38 | 0.44 | 0.01 | -0.02 | 0.12 | -0.03 | 0.12 | 0.46 | 0.18 | 0.06 | 0.43 |
| **D14** | 0.36 | 0.32 | 0.19 | 0.17 | 0.21 | 0.00 | 0.00 | 0.00 | 0.54 | 0.52 | 0.59 | 0.44 | 0.38 | — | **`0.95`** 🔴 | 0.03 | 0.05 | 0.15 | 0.24 | 0.41 | `0.60` 🟡 | 0.43 | 0.20 | 0.35 |
| **D15** | 0.24 | 0.25 | 0.23 | 0.20 | 0.25 | 0.00 | 0.00 | 0.00 | 0.59 | 0.43 | `0.61` 🟡 | 0.40 | 0.44 | **`0.95`** 🔴 | — | -0.00 | 0.00 | 0.12 | 0.10 | 0.26 | 0.57 | 0.42 | 0.14 | 0.29 |
| **D16** | 0.06 | -0.00 | 0.11 | 0.09 | 0.10 | 0.00 | 0.00 | 0.00 | 0.01 | 0.03 | -0.03 | 0.00 | 0.01 | 0.03 | -0.00 | — | 0.53 | 0.13 | 0.01 | 0.06 | 0.07 | -0.05 | 0.07 | -0.01 |
| **D17** | 0.07 | -0.05 | 0.08 | 0.06 | 0.08 | 0.00 | 0.00 | 0.00 | -0.04 | -0.02 | -0.02 | -0.01 | -0.02 | 0.05 | 0.00 | 0.53 | — | 0.06 | -0.02 | 0.02 | 0.11 | -0.08 | 0.06 | -0.02 |
| **D18** | 0.09 | 0.03 | 0.33 | 0.30 | 0.34 | 0.00 | 0.00 | 0.00 | 0.14 | 0.19 | 0.14 | 0.05 | 0.12 | 0.15 | 0.12 | 0.13 | 0.06 | — | 0.05 | 0.20 | 0.33 | 0.09 | 0.07 | 0.14 |
| **D19** | `0.67` 🟡 | `0.62` 🟡 | 0.16 | 0.09 | 0.16 | 0.00 | 0.00 | 0.00 | 0.00 | -0.05 | 0.14 | 0.06 | -0.03 | 0.24 | 0.10 | 0.01 | -0.02 | 0.05 | — | `0.67` 🟡 | 0.05 | 0.02 | 0.05 | -0.02 |
| **D20** | **`1.00`** 🔴 | 0.59 | 0.18 | 0.14 | 0.19 | 0.00 | 0.00 | 0.00 | 0.21 | 0.08 | 0.33 | 0.22 | 0.12 | 0.41 | 0.26 | 0.06 | 0.02 | 0.20 | `0.67` 🟡 | — | 0.28 | 0.23 | 0.20 | 0.05 |
| **D21** | 0.25 | 0.12 | 0.35 | 0.31 | 0.34 | 0.00 | 0.00 | 0.00 | 0.44 | 0.59 | 0.51 | 0.43 | 0.46 | `0.60` 🟡 | 0.57 | 0.07 | 0.11 | 0.33 | 0.05 | 0.28 | — | 0.39 | 0.10 | 0.15 |
| **D22** | 0.23 | 0.16 | 0.18 | 0.14 | 0.18 | 0.00 | 0.00 | 0.00 | 0.29 | 0.25 | 0.40 | 0.33 | 0.18 | 0.43 | 0.42 | -0.05 | -0.08 | 0.09 | 0.02 | 0.23 | 0.39 | — | 0.29 | 0.05 |
| **D23** | 0.13 | 0.06 | 0.29 | 0.13 | 0.29 | 0.00 | 0.00 | 0.00 | 0.09 | 0.10 | 0.12 | 0.12 | 0.06 | 0.20 | 0.14 | 0.07 | 0.06 | 0.07 | 0.05 | 0.20 | 0.10 | 0.29 | — | 0.16 |
| **D24** | -0.01 | -0.01 | -0.04 | 0.01 | -0.05 | 0.00 | 0.00 | 0.00 | 0.11 | 0.12 | 0.12 | 0.03 | 0.43 | 0.35 | 0.29 | -0.01 | -0.02 | 0.14 | -0.02 | 0.05 | 0.15 | 0.05 | 0.16 | — |

