# Submission Integrity Audit: `submission_01_fintech_report.pdf`

**Overall Assessment:** **🔴 HIGH INTEGRITY RISK**

**System Recommendation:** Critical internal peer similarity detected (66.7% meets or exceeds 50.0% threshold).

## 1. Multi-Signal Integrity Scores

| Signal Metric | Score | Decision Boundary Threshold |
| :--- | :---: | :---: |
| **Internal Peer-to-Peer Similarity** | **66.7%** | ≥ 50.0% (High), ≥ 20.0% (Medium) |
| **External / Reference Similarity** | **0.0%** | ≥ 40.0% (High), ≥ 20.0% (Medium) |
| **AI-Generated Content Likelihood** | **12.9%** | Probabilistic (≥ 80.0% Medium alone) |


## 2. Template & Common Prompt Filtering (Scenario 4)

*No recurring institutional boilerplate or prompt templates required discounting for this file.*

## 3. Multimodal Audio/Video Cross-Matches (Scenario 1)

Identified audio speech matching written submission passages:


### Match #1 — Target: `submission_02_video_pitch.mp4` (Similarity: **1.00** | **High-confidence match (>=0.80)**)
- **Query Location:** `Page 2`
- **Matched File Location:** `00:00:00 - 00:00:27`
- **Offending Query Spoken/Text:**
  > *"The core competitive advantage relies on vertical integration of credit underwriting models with real-time transactional payment gateways."*
- **Matched Counterpart:**
  > *"The core competitive advantage relies on vertical integration of credit underwriting models with real-time transactional payment gateways."*

## 4. Internal Peer Document Overlaps & Paraphrasing (Scenario 2)

### Overlap #1 — Target: `submission_20_partially_copied.docx` | **High-confidence match (>=0.80)**
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
| **RoBERTa Classifier (Supervised)** | 0.2% | Supervised synthetic classifier |
| **GPT-2 Perplexity (PPL)** | 77.17 | Lower PPL (<35) correlates with LLMs |
| **Sentence Burstiness (Length Variance)** | 25.97 | Lower burstiness (<35) indicates uniform machine cadence |
| **Composite AI Probability** | **12.9%** | Confidence: HIGH |

> [!NOTE]
> Probabilistic heuristic indicator. AI confidence alone never elevates risk to HIGH without corroborating external or peer matches.

## 7. Reviewer Rapid Decision Checklist (< 30 Seconds)

- [ ] Verify highlighted passages in Section 3/4 above against candidate submission.
- [ ] Confirm whether citation credit was omitted by author.
- [ ] **Action:** Initiate formal academic integrity escalation.