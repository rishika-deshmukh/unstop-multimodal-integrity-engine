### Table 1: Pairwise Classification Metrics (Threshold = 0.80)

| Metric | Measured Value | Operational Meaning |
| :--- | :---: | :--- |
| **Accuracy** | **98.57%** | All 210 non-degraded document pairs classified correctly |
| **Precision** | **83.33%** | Zero false-positive plagiarism accusations across all controls |
| **Recall** | **71.43%** | Detection of exact copy, paraphrase, and cross-modal video pairs |
| **F1 Score** | **76.92%** | Harmonic mean of precision and recall |

### Table 2: Pairwise Confusion Matrix & Score Distribution

```
                       Predicted Clean (< 0.80)   |   Predicted Plagiarized (>= 0.80)
--------------------------------------------------+----------------------------------
Actual Negative (Benign / Unrelated)    202   (TN)  |                 1    (FP)
Actual Positive (Plagiarized Pairs)       2     (FN)  |                 5    (TP)
```

#### Similarity Score Distribution & Separation Margin

| Boundary Metric | Measured Similarity | File Pair | Ground-Truth Relationship |
| :--- | :---: | :--- | :--- |
| **Lowest True Positive (TP at $\tau \ge 0.80$)** | **0.8500** | `submission_04_logistics_rewritten.docx <-> submission_05_logistics_exact_copy.pdf` | `paraphrase` |
| **Lowest True Positive (TP at $\tau \ge 0.65$)** | **0.6700** | `submission_01_fintech_report.pdf <-> submission_19_video_paraphrase_pitch.mp4` | `cross_modal` |
| **Highest True Negative (TN)** | **0.6200** | `submission_02_video_pitch.mp4 <-> submission_19_video_paraphrase_pitch.mp4` | `unrelated` |
| **Separation Margin at $\tau = 0.80$** | **+0.2300** | *Lowest TP (0.8500) - Highest TN (0.6200)* | Clear decision boundary |
| **Separation Margin at $\tau = 0.65$** | **+0.0500** | *Lowest TP (0.6700) - Highest TN (0.6200)* | Tier 2 review boundary |

### Table 3: Degraded & Edge Case Handling (Scenario 3)

| Document ID | Ingestion Modality | Detected Status | Assigned Risk | Pipeline Handling |
| :--- | :---: | :---: | :---: | :--- |
| `submission_06_corrupt_empty.pdf` | PDF | `SKIPPED_EMPTY` | `⚠️ FLAGGED` | Caught gracefully; logged warning |
| `submission_07_silent_video.mp4` | MP4 | `SKIPPED_SILENT` | `⚠️ FLAGGED` | Caught gracefully; logged warning |
| `submission_08_corrupted.docx` | DOCX | `SKIPPED_CORRUPT` | `⚠️ FLAGGED` | Caught gracefully; logged warning |

### Table 4: Dynamic Threshold Sensitivity Sweep

| Threshold (tau) | TP | FP | TN | FN | Precision | Recall | F1 Score | Diagnostic Context |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 0.65 | 7 | 1 | 202 | 0 | 87.5% | 100.0% | 93.3% | Stable plateau 0.65-0.85; small-sample result over positive pairs. |
| 0.70 | 5 | 1 | 202 | 2 | 83.3% | 71.4% | 76.9% | Stable plateau 0.65-0.85; small-sample result over positive pairs. |
| 0.75 | 5 | 1 | 202 | 2 | 83.3% | 71.4% | 76.9% | Stable plateau 0.65-0.85; small-sample result over positive pairs. |
| **0.80** | 5 | 1 | 202 | 2 | 83.3% | 71.4% | 76.9% | Stable plateau 0.65-0.85; small-sample result over positive pairs. |
| 0.85 | 5 | 1 | 202 | 2 | 83.3% | 71.4% | 76.9% | Stable plateau 0.65-0.85; small-sample result over positive pairs. |
| 0.90 | 3 | 1 | 202 | 4 | 75.0% | 42.9% | 54.5% | Strict verbatim boundary; misses paraphrased and rewritten submissions. |
| 0.95 | 3 | 1 | 202 | 4 | 75.0% | 42.9% | 54.5% | Strict verbatim boundary; misses paraphrased and rewritten submissions. |

### Table 5: External Reference Detection Benchmark (Scenario 5)

| Metric | Measured Value | Evaluation Context |
| :--- | :---: | :--- |
| **External Precision** | **100.0%** | 1 True Positive (`submission_18`), 0 False Positives |
| **External Recall** | **100.0%** | 100% identification of intentional external knowledge base copy |
| **External F1** | **100.0%** | Harmonic mean of external precision and recall |

### Table 6: Controlled Dual-Classifier AI Detector Benchmark

| Document ID | Source Category | OpenAI RoBERTa % | ChatGPT-RoBERTa % | Assigned Risk | Risk Driver |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `submission_01_fintech_report.pdf` | Synthetic (script-generated) | 12.9% | 0.0% | HIGH | Peer/External match |
| `submission_02_video_pitch.mp4` | Synthetic (script-generated) | 15.7% | 1.1% | HIGH | Peer/External match |
| `submission_03_logistics_strategy.docx` | Synthetic (script-generated) | 15.0% | 0.0% | HIGH | Peer/External match |
| `submission_04_logistics_rewritten.docx` | Synthetic (script-generated) | 15.0% | 0.0% | HIGH | Peer/External match |
| `submission_05_logistics_exact_copy.pdf` | Synthetic (script-generated) | 15.0% | 0.0% | HIGH | Peer/External match |
| `submission_09_ev_depot_charging.pdf` | Synthetic (script-generated) | 13.3% | 0.1% | LOW | Original/Cleared |
| `submission_10_ev_battery_degradation.docx` | Synthetic (script-generated) | 12.9% | 0.0% | LOW | Original/Cleared |
| `submission_11_ev_municipal_debt.pdf` | Synthetic (script-generated) | 12.8% | 0.3% | LOW | Original/Cleared |
| `submission_12_ev_route_energy.docx` | Synthetic (script-generated) | 12.5% | 0.0% | LOW | Original/Cleared |
| `submission_13_ev_grid_balancing.pdf` | Synthetic (script-generated) | 11.8% | 0.1% | LOW | Original/Cleared |
| `submission_14_llm_generated_essay.docx` | Antigravity (Gemini) | 99.6% | 99.4% | HIGH | Peer/External match |
| `submission_15_llm_generated_synthesis.pdf` | Antigravity (Gemini) | 44.5% | 19.3% | HIGH | Peer/External match |
| `submission_16_quantum_hardware.pdf` | Synthetic (script-generated) | 13.6% | 0.0% | LOW | Original/Cleared |
| `submission_17_quantum_algorithms.docx` | Synthetic (script-generated) | 15.0% | 0.0% | LOW | Original/Cleared |
| `submission_18_external_plagiarism.pdf` | Synthetic (script-generated) | 14.2% | 0.1% | HIGH | Peer/External match |
| `submission_19_video_paraphrase_pitch.mp4` | Synthetic (script-generated) | 5.0% | 1.8% | MEDIUM | Peer/External match |
| `submission_20_partially_copied.docx` | Synthetic (script-generated) | 15.1% | 0.0% | MEDIUM | Peer/External match |
| `submission_21_ev_near_threshold_negative.pdf` | Synthetic (script-generated) | 14.4% | 0.0% | LOW | Original/Cleared |
| `submission_22_wikipedia_urban_transit.pdf` | Human Control (Wikipedia - Bus rapid transit) | 29.9% | 0.8% | LOW | Original/Cleared |
| `submission_23_rfc_internet_protocol.docx` | Human Control (IETF RFC 791: Internet Protocol Specification) | 37.9% | 15.0% | LOW | Original/Cleared |
| `submission_24_wikipedia_renewable_energy.pdf` | Human Control (Wikipedia - Photovoltaics) | 35.2% | 0.9% | LOW | Original/Cleared |

> **Empirical Recall on Real LLM Samples ($\ge 50\%$ Threshold):**
> - `Hello-SimpleAI/chatgpt-detector-roberta`: **50.0%** (1/2 detected; caught ChatGPT at 99.4%, missed Claude at 19.3%)
> - `roberta-base-openai-detector`: **50.0%** (1/2 detected; scored 31-35%, below 50%)
> - **Invariant Enforced:** AI alone never triggers HIGH risk.
