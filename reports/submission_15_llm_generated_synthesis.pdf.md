# Submission Integrity Audit: `submission_15_llm_generated_synthesis.pdf`

**Overall Assessment:** **🔴 HIGH INTEGRITY RISK**

**System Recommendation:** Critical internal peer similarity detected (62.5% meets or exceeds 50.0% threshold). | Reviewer note: High semantic similarity between AI-generated submissions may stem from independent generation using an identical assignment prompt rather than direct student-to-student copying.

## 1. Multi-Signal Integrity Scores

| Signal Metric | Score | Decision Boundary Threshold |
| :--- | :---: | :---: |
| **Internal Peer-to-Peer Similarity** | **62.5%** | ≥ 50.0% (High), ≥ 20.0% (Medium) |
| **External / Reference Similarity** | **0.0%** | ≥ 40.0% (High), ≥ 20.0% (Medium) |
| **AI-Generated Content Likelihood** | **44.5%** | Probabilistic (≥ 80.0% Medium alone) |


## 2. Template & Common Prompt Filtering (Scenario 4)

*No recurring institutional boilerplate or prompt templates required discounting for this file.*

## 3. Multimodal Audio/Video Cross-Matches (Scenario 1)

*No cross-modal speech-to-text overlaps detected.*

## 4. Internal Peer Document Overlaps & Paraphrasing (Scenario 2)

### Overlap #1 — Target: `submission_14_llm_generated_essay.docx` | **High-confidence match (>=0.80)**
| Semantic Cosine Sim | Lexical Jaccard Sim | Levenshtein Sim | Page References |
| :---: | :---: | :---: | :---: |
| **0.90** | **0.57** | **0.61** | Query: Pg 1 ↔ Match: Pg 1 |
- **Query Passage:**
  > *"Business Case Analysis: EV Bus Fleet Charging Costs
The transition from diesel-powered buses to electric vehicles (EVs) presents a significant opportunity for public transportation operators to reduce operating expenses, improve environmental sustainability, and modernize fleet operations."*
- **Matched Source Passage:**
  > *"The transition from diesel-powered buses to electric vehicle (EV) buses presents a significant opportunity for public transportation operators to reduce operating costs, improve energy efficiency, and achieve sustainability targets."*

### Overlap #2 — Target: `submission_14_llm_generated_essay.docx` | **High-confidence match (>=0.80)**
| Semantic Cosine Sim | Lexical Jaccard Sim | Levenshtein Sim | Page References |
| :---: | :---: | :---: | :---: |
| **0.90** | **0.79** | **0.71** | Query: Pg 1 ↔ Match: Pg 1 |
- **Query Passage:**
  > *"Cost Structure and Key Considerations
The primary advantage of EV buses is their lower energy cost compared to diesel consumption."*
- **Matched Source Passage:**
  > *"The primary advantage of EV buses is their lower energy cost compared to diesel consumption."*

### Overlap #3 — Target: `submission_14_llm_generated_essay.docx` ⚠️ **[SYNONYM-BASED PARAPHRASE DETECTED]** | **Possible paraphrase / review recommended (0.65-0.79)**
| Semantic Cosine Sim | Lexical Jaccard Sim | Levenshtein Sim | Page References |
| :---: | :---: | :---: | :---: |
| **0.71** | **0.17** | **0.28** | Query: Pg 1 ↔ Match: Pg 1 |
> **Reviewer Note:** High dense embedding similarity (>0.80) with low lexical Jaccard (<0.35) confirms semantic rewriting evasion.
- **Query Passage:**
  > *"The total charging cost depends on battery capacity, distance travelled, energy consumption per kilometre, electricity tariffs, and charging efficiency."*
- **Matched Source Passage:**
  > *"However, electricity costs vary depending on charging schedules, commercial tariffs, demand charges, and peak-hour pricing."*

### Overlap #4 — Target: `submission_14_llm_generated_essay.docx` | **Possible paraphrase / review recommended (0.65-0.79)**
| Semantic Cosine Sim | Lexical Jaccard Sim | Levenshtein Sim | Page References |
| :---: | :---: | :---: | :---: |
| **0.75** | **0.38** | **0.35** | Query: Pg 2 ↔ Match: Pg 1 |
- **Query Passage:**
  > *"Infrastructure and Operational Costs
Beyond electricity expenses, operators must invest in charging stations, transformers, grid connections, battery management systems, and maintenance."*
- **Matched Source Passage:**
  > *"Costs include installing charging stations, upgrading electrical connections, transformers, power distribution systems, and battery management infrastructure."*

### Overlap #5 — Target: `submission_14_llm_generated_essay.docx` | **High-confidence match (>=0.80)**
| Semantic Cosine Sim | Lexical Jaccard Sim | Levenshtein Sim | Page References |
| :---: | :---: | :---: | :---: |
| **0.85** | **0.39** | **0.58** | Query: Pg 2 ↔ Match: Pg 1 |
- **Query Passage:**
  > *"- Renewable Integration: Use rooftop solar installations and battery storage to reduce grid dependency."*
- **Matched Source Passage:**
  > *"- Renewable energy: Integrate rooftop solar or renewable electricity procurement to reduce grid dependency."*

### Overlap #6 — Target: `submission_14_llm_generated_essay.docx` | **High-confidence match (>=0.80)**
| Semantic Cosine Sim | Lexical Jaccard Sim | Levenshtein Sim | Page References |
| :---: | :---: | :---: | :---: |
| **0.95** | **0.54** | **0.44** | Query: Pg 2 ↔ Match: Pg 1 |
- **Query Passage:**
  > *"4. Business Impact and Recommendations
Although EV buses require higher initial investments, their lower energy and maintenance costs can generate long-term savings."*
- **Matched Source Passage:**
  > *"Although EV buses involve higher upfront acquisition and infrastructure costs, their lower energy and maintenance expenses can generate substantial long-term savings."*

### Overlap #7 — Target: `submission_14_llm_generated_essay.docx` ⚠️ **[SYNONYM-BASED PARAPHRASE DETECTED]** | **High-confidence match (>=0.80)**
| Semantic Cosine Sim | Lexical Jaccard Sim | Levenshtein Sim | Page References |
| :---: | :---: | :---: | :---: |
| **0.83** | **0.21** | **0.29** | Query: Pg 2 ↔ Match: Pg 1 |
> **Reviewer Note:** High dense embedding similarity (>0.80) with low lexical Jaccard (<0.35) confirms semantic rewriting evasion.
- **Query Passage:**
  > *"Implementing smart charging systems, renewable energy integration, and data-driven fleet management can significantly improve financial viability."*
- **Matched Source Passage:**
  > *"A data-driven charging strategy can reduce operating expenditure, improve fleet utilisation, and strengthen the long-term economic and environmental sustainability of public transportation."*

## 5. External Knowledge Base & Web References

*No uncredited external reference matches detected.*

## 6. AI-Generation Signal Breakdown (Requirement 7)

| Component | Estimated Value | Interpretation |
| :--- | :---: | :--- |
| **RoBERTa Classifier (Supervised)** | 20.3% | Supervised synthetic classifier |
| **GPT-2 Perplexity (PPL)** | 27.35 | Lower PPL (<35) correlates with LLMs |
| **Sentence Burstiness (Length Variance)** | 19.02 | Lower burstiness (<35) indicates uniform machine cadence |
| **Composite AI Probability** | **44.5%** | Confidence: MODERATE |

> [!NOTE]
> Probabilistic heuristic indicator. AI confidence alone never elevates risk to HIGH without corroborating external or peer matches.

## 7. Reviewer Rapid Decision Checklist (< 30 Seconds)

- [ ] Verify highlighted passages in Section 3/4 above against candidate submission.
- [ ] Confirm whether citation credit was omitted by author.
- [ ] **Action:** Initiate formal academic integrity escalation.