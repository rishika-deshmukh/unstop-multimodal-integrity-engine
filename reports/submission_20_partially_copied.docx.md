# Submission Integrity Audit: `submission_20_partially_copied.docx`

**Overall Assessment:** **🟡 MEDIUM INTEGRITY RISK**

**System Recommendation:** Moderate peer overlap detected (33.3% meets or exceeds 20.0% threshold). Mutual overlap detected (direction undetermined); candidate submission may be the original source copied by another peer rather than the copier. Reviewer manual verification required before penalizing.

## 1. Multi-Signal Integrity Scores

| Signal Metric | Score | Decision Boundary Threshold |
| :--- | :---: | :---: |
| **Internal Peer-to-Peer Similarity** | **33.3%** | ≥ 50.0% (High), ≥ 20.0% (Medium) |
| **External / Reference Similarity** | **0.0%** | ≥ 40.0% (High), ≥ 20.0% (Medium) |
| **AI-Generated Content Likelihood** | **15.1%** | Probabilistic (≥ 80.0% Medium alone) |


## 2. Template & Common Prompt Filtering (Scenario 4)

*No recurring institutional boilerplate or prompt templates required discounting for this file.*

## 3. Multimodal Audio/Video Cross-Matches (Scenario 1)

*No cross-modal speech-to-text overlaps detected.*

## 4. Internal Peer Document Overlaps & Paraphrasing (Scenario 2)

### Overlap #1 — Target: `submission_01_fintech_report.pdf` | **High-confidence match (>=0.80)**
| Semantic Cosine Sim | Lexical Jaccard Sim | Levenshtein Sim | Page References |
| :---: | :---: | :---: | :---: |
| **1.00** | **1.00** | **1.00** | Query: Pg 1 ↔ Match: Pg 1 |
- **Query Passage:**
  > *"Modern digital credit infrastructure enables instantaneous risk assessment for underserved consumer segments by ingesting alternative transactional data streams including utility bill remittances and mobile airtime top-ups."*
- **Matched Source Passage:**
  > *"Modern digital credit infrastructure enables instantaneous risk assessment for underserved consumer segments by ingesting alternative transactional data streams including utility bill remittances and mobile airtime top-ups."*

## 5. External Knowledge Base & Web References

*No uncredited external reference matches detected.*

## 6. AI-Generation Signal Breakdown (Requirement 7)

| Component | Estimated Value | Interpretation |
| :--- | :---: | :--- |
| **RoBERTa Classifier (Supervised)** | 0.1% | Supervised synthetic classifier |
| **GPT-2 Perplexity (PPL)** | 96.39 | Lower PPL (<35) correlates with LLMs |
| **Sentence Burstiness (Length Variance)** | 17.82 | Lower burstiness (<35) indicates uniform machine cadence |
| **Composite AI Probability** | **15.1%** | Confidence: HIGH |

> [!NOTE]
> Probabilistic heuristic indicator. AI confidence alone never elevates risk to HIGH without corroborating external or peer matches.

## 7. Reviewer Rapid Decision Checklist (< 30 Seconds)

- [ ] Check whether similarity is due to common domain definitions or LLM drafting assistance.
- [ ] **Action:** Request clarification from candidate or second reviewer inspection.