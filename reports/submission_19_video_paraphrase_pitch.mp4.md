# Submission Integrity Audit: `submission_19_video_paraphrase_pitch.mp4`

**Overall Assessment:** **🟡 MEDIUM INTEGRITY RISK**

**System Recommendation:** Possible paraphrase detected: Tier 2 similarity (0.67 in 0.65-0.80 range); manual review recommended before concluding integrity violation.

## 1. Multi-Signal Integrity Scores

| Signal Metric | Score | Decision Boundary Threshold |
| :--- | :---: | :---: |
| **Internal Peer-to-Peer Similarity** | **0.0%** | ≥ 50.0% (High), ≥ 20.0% (Medium) |
| **External / Reference Similarity** | **0.0%** | ≥ 40.0% (High), ≥ 20.0% (Medium) |
| **AI-Generated Content Likelihood** | **5.0%** | Probabilistic (≥ 80.0% Medium alone) |


## 2. Template & Common Prompt Filtering (Scenario 4)

*No recurring institutional boilerplate or prompt templates required discounting for this file.*

## 3. Multimodal Audio/Video Cross-Matches (Scenario 1)

Identified audio speech matching written submission passages:


### Match #1 — Target: `submission_20_partially_copied.docx` (Similarity: **0.67** | **Possible paraphrase / review recommended (0.65-0.79)**)
- **Query Location:** `00:00:00 - 00:00:17`
- **Matched File Location:** `Page 1`
- **Offending Query Spoken/Text:**
  > *"Digital Microfinance providers in emerging economies utilize algorithmic credit scoring"*
- **Matched Counterpart:**
  > *"Digital Banking Infrastructure and Microfinance Expansion."*

## 4. Internal Peer Document Overlaps & Paraphrasing (Scenario 2)

*No internal peer document plagiarism detected.*

## 5. External Knowledge Base & Web References

*No uncredited external reference matches detected.*

## 6. AI-Generation Signal Breakdown (Requirement 7)

| Component | Estimated Value | Interpretation |
| :--- | :---: | :--- |
| **RoBERTa Classifier (Supervised)** | 1.9% | Supervised synthetic classifier |
| **GPT-2 Perplexity (PPL)** | 226.89 | Lower PPL (<35) correlates with LLMs |
| **Sentence Burstiness (Length Variance)** | 50.00 | Lower burstiness (<35) indicates uniform machine cadence |
| **Composite AI Probability** | **5.0%** | Confidence: HIGH |

> [!NOTE]
> Probabilistic heuristic indicator. AI confidence alone never elevates risk to HIGH without corroborating external or peer matches.

## 7. Reviewer Rapid Decision Checklist (< 30 Seconds)

- [ ] Check whether similarity is due to common domain definitions or LLM drafting assistance.
- [ ] **Action:** Request clarification from candidate or second reviewer inspection.