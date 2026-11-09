# Submission Integrity Audit: `submission_03_logistics_strategy.docx`

**Overall Assessment:** **🔴 HIGH INTEGRITY RISK**

**System Recommendation:** Critical internal peer similarity detected (50.0% exceeds 50.0% threshold).

## 1. Multi-Signal Integrity Scores

| Signal Metric | Score | Decision Boundary Threshold |
| :--- | :---: | :---: |
| **Internal Peer-to-Peer Similarity** | **50.0%** | ≥ 50.0% (High), ≥ 20.0% (Medium) |
| **External / Reference Similarity** | **50.0%** | ≥ 40.0% (High), ≥ 20.0% (Medium) |
| **AI-Generated Content Likelihood** | **28.5%** | Probabilistic (≥ 80.0% Medium alone) |


## 2. Template & Common Prompt Filtering (Scenario 4)

*No recurring institutional boilerplate or prompt templates required discounting for this file.*

## 3. Multimodal Audio/Video Cross-Matches (Scenario 1)

*No cross-modal speech-to-text overlaps detected.*

## 4. Internal Peer Document Overlaps & Paraphrasing (Scenario 2)

### Overlap #1 — Target: `submission_04_logistics_rewritten.docx` ⚠️ **[SYNONYM-BASED PARAPHRASE DETECTED]**
| Semantic Cosine Sim | Lexical Jaccard Sim | Levenshtein Sim | Page References |
| :---: | :---: | :---: | :---: |
| **0.87** | **0.18** | **0.49** | Query: Pg 1 ↔ Match: Pg 1 |
> **Reviewer Note:** High dense embedding similarity (>0.80) with low lexical Jaccard (<0.35) confirms semantic rewriting evasion.
- **Query Passage:**
  > *"Active refrigeration containers utilizing automated compressor cycles guarantee temperature stability during transcontinental flights, whereas passive thermal shippers rely on vacuum-insulated panels to protect vaccines during domestic road haulage."*
- **Matched Source Passage:**
  > *"Active refrigerated enclosures deploying computerized cooling mechanisms ensure temperature consistency during international flight segments, while passive temperature-safe boxes depend on vacuum-insulated panels to safeguard vaccine vials throughout ground truck transport."*

## 5. External Knowledge Base & Web References

- **Source:** [Temperature-Controlled Pharmaceutical Supply Chain Infrastructure](https://en.wikipedia.org/wiki/Cold_chain) (Cosine Sim: **0.81**)
  - **Submission Text:** *"Establishing a resilient pharmaceutical cold chain requires continuous thermal monitoring between two and eight degrees Celsius across all intermediate warehouse hubs."*
  - **Reference Text:** *"Pharmaceutical cold chain logistics necessitate strict end-to-end temperature preservation ranging from ultra-cold cryopreservation between minus eighty degrees Celsius to standardized refrigerated storage between two and eight degrees Celsius."*

## 6. AI-Generation Signal Breakdown (Requirement 7)

| Component | Estimated Value | Interpretation |
| :--- | :---: | :--- |
| **RoBERTa Classifier (Supervised)** | 20.7% | Supervised synthetic classifier |
| **GPT-2 Perplexity (PPL)** | 144.39 | Lower PPL (<35) correlates with LLMs |
| **Sentence Burstiness (Length Variance)** | 15.54 | Lower burstiness (<35) indicates uniform machine cadence |
| **Composite AI Probability** | **28.5%** | Confidence: MODERATE |

> [!NOTE]
> Probabilistic heuristic indicator. AI confidence alone never elevates risk to HIGH without corroborating external or peer matches.

## 7. Reviewer Rapid Decision Checklist (< 30 Seconds)

- [ ] Verify highlighted passages in Section 3/4 above against candidate submission.
- [ ] Confirm whether citation credit was omitted by author.
- [ ] **Action:** Initiate formal academic integrity escalation.