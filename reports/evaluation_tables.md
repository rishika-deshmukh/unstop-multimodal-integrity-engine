### Table 1: Pairwise Classification Metrics (Threshold = 0.80)

| Metric | Measured Value | Operational Meaning |
| :--- | :---: | :--- |
| **Accuracy** | **100.00%** | All 105 non-degraded document pairs classified correctly |
| **Precision** | **100.00%** | Zero false-positive plagiarism accusations across all controls |
| **Recall** | **100.00%** | Detection of exact copy, paraphrase, and cross-modal video pairs |
| **F1 Score** | **100.00%** | Harmonic mean of precision and recall |

### Table 2: Pairwise Confusion Matrix

```
                       Predicted Clean (< 0.80)   |   Predicted Plagiarized (>= 0.80)
--------------------------------------------------+----------------------------------
Actual Negative (Benign / Unrelated)    100   (TN)  |                 0    (FP)
Actual Positive (Plagiarized Pairs)       0     (FN)  |                 5    (TP)
```

### Table 3: Degraded & Edge Case Handling (Scenario 3)

| Document ID | Ingestion Modality | Detected Status | Assigned Risk | Pipeline Handling |
| :--- | :---: | :---: | :---: | :--- |
| `submission_06_corrupt_empty.pdf` | PDF | `SKIPPED_EMPTY` | `⚠️ FLAGGED` | Caught gracefully; logged warning |
| `submission_07_silent_video.mp4` | MP4 | `SKIPPED_SILENT` | `⚠️ FLAGGED` | Caught gracefully; logged warning |
| `submission_08_corrupted.docx` | DOCX | `SKIPPED_CORRUPT` | `⚠️ FLAGGED` | Caught gracefully; logged warning |

### Table 4: Dynamic Threshold Sensitivity Sweep

| Threshold ($	au$) | TP | FP | TN | FN | Precision | Recall | F1 Score | Diagnostic Context |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 0.65 | 5 | 0 | 100 | 0 | 100.0% | 100.0% | 100.0% | Stable plateau 0.65-0.85; small-sample result over positive pairs. |
| 0.70 | 5 | 0 | 100 | 0 | 100.0% | 100.0% | 100.0% | Stable plateau 0.65-0.85; small-sample result over positive pairs. |
| 0.75 | 5 | 0 | 100 | 0 | 100.0% | 100.0% | 100.0% | Stable plateau 0.65-0.85; small-sample result over positive pairs. |
| **0.80** | 5 | 0 | 100 | 0 | 100.0% | 100.0% | 100.0% | Stable plateau 0.65-0.85; small-sample result over positive pairs. |
| 0.85 | 5 | 0 | 100 | 0 | 100.0% | 100.0% | 100.0% | Stable plateau 0.65-0.85; small-sample result over positive pairs. |
| 0.90 | 3 | 0 | 100 | 2 | 100.0% | 60.0% | 75.0% | Strict verbatim boundary; misses paraphrased and rewritten submissions. |
| 0.95 | 3 | 0 | 100 | 2 | 100.0% | 60.0% | 75.0% | Strict verbatim boundary; misses paraphrased and rewritten submissions. |

### Table 5: External Reference Detection Benchmark (Scenario 5)

| Metric | Measured Value | Evaluation Context |
| :--- | :---: | :--- |
| **External Precision** | **33.3%** | 1 True Positive (`submission_18`), 2 False Positives (`submission_03`, `submission_05`) |
| **External Recall** | **100.0%** | 100% identification of intentional Wikipedia external copy |
| **External F1** | **50.0%** | Impacted by reference KB domain overlap with logistics strategy |

### Table 6: Controlled Dual-Classifier AI Detector Benchmark

| Document ID | Source Category | OpenAI RoBERTa % | ChatGPT-RoBERTa % | Assigned Risk | Risk Driver |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `submission_01_fintech_report.pdf` | Synthetic (script-generated) | 12.8% | 0.0% | MEDIUM | Peer/External match |
| `submission_02_video_pitch.mp4` | Synthetic (script-generated) | 26.4% | 1.6% | HIGH | Peer/External match |
| `submission_03_logistics_strategy.docx` | Synthetic (script-generated) | 28.5% | 0.0% | HIGH | Peer/External match |
| `submission_04_logistics_rewritten.docx` | Synthetic (script-generated) | 72.8% | 0.0% | HIGH | Peer/External match |
| `submission_05_logistics_exact_copy.pdf` | Synthetic (script-generated) | 26.0% | 0.0% | HIGH | Peer/External match |
| `submission_09_ev_depot_charging.pdf` | Synthetic (script-generated) | 13.2% | 0.1% | LOW | Original/Cleared |
| `submission_10_ev_battery_degradation.docx` | Synthetic (script-generated) | 12.8% | 0.0% | LOW | Original/Cleared |
| `submission_11_ev_municipal_debt.pdf` | Synthetic (script-generated) | 12.6% | 0.3% | LOW | Original/Cleared |
| `submission_12_ev_route_energy.docx` | Synthetic (script-generated) | 12.5% | 0.0% | LOW | Original/Cleared |
| `submission_13_ev_grid_balancing.pdf` | Synthetic (script-generated) | 11.7% | 0.1% | LOW | Original/Cleared |
| `submission_14_chatgpt_essay.docx` | ChatGPT (GPT-4o) | 35.0% | 99.4% | HIGH | Peer/External match |
| `submission_15_claude_synthesis.pdf` | Claude 3.5 Sonnet | 31.4% | 19.3% | HIGH | Peer/External match |
| `submission_16_quantum_hardware.pdf` | Synthetic (script-generated) | 13.6% | 0.0% | LOW | Original/Cleared |
| `submission_17_quantum_algorithms.docx` | Synthetic (script-generated) | 15.1% | 0.0% | LOW | Original/Cleared |
| `submission_18_external_plagiarism.pdf` | Synthetic (script-generated) | 14.5% | 0.1% | HIGH | Peer/External match |

> **Empirical Recall on Real LLM Samples ($\ge 50\%$ Threshold):**
> - `Hello-SimpleAI/chatgpt-detector-roberta`: **50.0%** (1/2 detected; caught ChatGPT at 99.4%, missed Claude at 19.3%)
> - `roberta-base-openai-detector`: **0.0%** (0/2 detected; scored 31-35%, below 50%)
> - **Invariant Enforced:** AI alone never triggers HIGH risk.
