# Submission Integrity Audit: `submission_14_llm_generated_essay.docx`

**Overall Assessment:** **🔴 HIGH INTEGRITY RISK**

**System Recommendation:** Critical internal peer similarity detected (62.5% meets or exceeds 50.0% threshold).

## 1. Multi-Signal Integrity Scores

| Signal Metric | Score | Decision Boundary Threshold |
| :--- | :---: | :---: |
| **Internal Peer-to-Peer Similarity** | **62.5%** | ≥ 50.0% (High), ≥ 20.0% (Medium) |
| **External / Reference Similarity** | **0.0%** | ≥ 40.0% (High), ≥ 20.0% (Medium) |
| **AI-Generated Content Likelihood** | **99.6%** | Probabilistic (≥ 80.0% Medium alone) |


## 2. Template & Common Prompt Filtering (Scenario 4)

*No recurring institutional boilerplate or prompt templates required discounting for this file.*

## 3. Multimodal Audio/Video Cross-Matches (Scenario 1)

*No cross-modal speech-to-text overlaps detected.*

## 4. Internal Peer Document Overlaps & Paraphrasing (Scenario 2)

### Overlap #1 — Target: `submission_15_llm_generated_synthesis.pdf` | **High-confidence match (>=0.80)**
| Semantic Cosine Sim | Lexical Jaccard Sim | Levenshtein Sim | Page References |
| :---: | :---: | :---: | :---: |
| **0.90** | **0.57** | **0.61** | Query: Pg 1 ↔ Match: Pg 1 |
- **Query Passage:**
  > *"The transition from diesel-powered buses to electric vehicle (EV) buses presents a significant opportunity for public transportation operators to reduce operating costs, improve energy efficiency, and achieve sustainability targets."*
- **Matched Source Passage:**
  > *"Business Case Analysis: EV Bus Fleet Charging Costs
The transition from diesel-powered buses to electric vehicles (EVs) presents a significant opportunity for public transportation operators to reduce operating expenses, improve environmental sustainability, and modernize fleet operations."*

### Overlap #2 — Target: `submission_15_llm_generated_synthesis.pdf` | **High-confidence match (>=0.80)**
| Semantic Cosine Sim | Lexical Jaccard Sim | Levenshtein Sim | Page References |
| :---: | :---: | :---: | :---: |
| **0.90** | **0.79** | **0.71** | Query: Pg 1 ↔ Match: Pg 1 |
- **Query Passage:**
  > *"The primary advantage of EV buses is their lower energy cost compared to diesel consumption."*
- **Matched Source Passage:**
  > *"Cost Structure and Key Considerations
The primary advantage of EV buses is their lower energy cost compared to diesel consumption."*

### Overlap #3 — Target: `submission_15_llm_generated_synthesis.pdf` ⚠️ **[SYNONYM-BASED PARAPHRASE DETECTED]** | **Possible paraphrase / review recommended (0.65-0.79)**
| Semantic Cosine Sim | Lexical Jaccard Sim | Levenshtein Sim | Page References |
| :---: | :---: | :---: | :---: |
| **0.71** | **0.17** | **0.28** | Query: Pg 1 ↔ Match: Pg 1 |
> **Reviewer Note:** High dense embedding similarity (>0.80) with low lexical Jaccard (<0.35) confirms semantic rewriting evasion.
- **Query Passage:**
  > *"However, electricity costs vary depending on charging schedules, commercial tariffs, demand charges, and peak-hour pricing."*
- **Matched Source Passage:**
  > *"The total charging cost depends on battery capacity, distance travelled, energy consumption per kilometre, electricity tariffs, and charging efficiency."*

### Overlap #4 — Target: `submission_15_llm_generated_synthesis.pdf` ⚠️ **[SYNONYM-BASED PARAPHRASE DETECTED]** | **Possible paraphrase / review recommended (0.65-0.79)**
| Semantic Cosine Sim | Lexical Jaccard Sim | Levenshtein Sim | Page References |
| :---: | :---: | :---: | :---: |
| **0.80** | **0.07** | **0.19** | Query: Pg 1 ↔ Match: Pg 1 |
> **Reviewer Note:** High dense embedding similarity (>0.80) with low lexical Jaccard (<0.35) confirms semantic rewriting evasion.
- **Query Passage:**
  > *"Establishing an EV bus charging network requires substantial initial investment."*
- **Matched Source Passage:**
  > *"Business Case Analysis: EV Bus Fleet Charging Costs
The transition from diesel-powered buses to electric vehicles (EVs) presents a significant opportunity for public transportation operators to reduce operating expenses, improve environmental sustainability, and modernize fleet operations."*

### Overlap #5 — Target: `submission_15_llm_generated_synthesis.pdf` | **High-confidence match (>=0.80)**
| Semantic Cosine Sim | Lexical Jaccard Sim | Levenshtein Sim | Page References |
| :---: | :---: | :---: | :---: |
| **0.85** | **0.39** | **0.58** | Query: Pg 1 ↔ Match: Pg 2 |
- **Query Passage:**
  > *"- Renewable energy: Integrate rooftop solar or renewable electricity procurement to reduce grid dependency."*
- **Matched Source Passage:**
  > *"- Renewable Integration: Use rooftop solar installations and battery storage to reduce grid dependency."*

### Overlap #6 — Target: `submission_15_llm_generated_synthesis.pdf` | **High-confidence match (>=0.80)**
| Semantic Cosine Sim | Lexical Jaccard Sim | Levenshtein Sim | Page References |
| :---: | :---: | :---: | :---: |
| **0.95** | **0.54** | **0.44** | Query: Pg 1 ↔ Match: Pg 2 |
- **Query Passage:**
  > *"Although EV buses involve higher upfront acquisition and infrastructure costs, their lower energy and maintenance expenses can generate substantial long-term savings."*
- **Matched Source Passage:**
  > *"4. Business Impact and Recommendations
Although EV buses require higher initial investments, their lower energy and maintenance costs can generate long-term savings."*

### Overlap #7 — Target: `submission_15_llm_generated_synthesis.pdf` ⚠️ **[SYNONYM-BASED PARAPHRASE DETECTED]** | **High-confidence match (>=0.80)**
| Semantic Cosine Sim | Lexical Jaccard Sim | Levenshtein Sim | Page References |
| :---: | :---: | :---: | :---: |
| **0.85** | **0.12** | **0.25** | Query: Pg 1 ↔ Match: Pg 1 |
> **Reviewer Note:** High dense embedding similarity (>0.80) with low lexical Jaccard (<0.35) confirms semantic rewriting evasion.
- **Query Passage:**
  > *"EV bus fleet electrification is a financially promising investment when supported by efficient charging infrastructure and intelligent energy management."*
- **Matched Source Passage:**
  > *"Business Case Analysis: EV Bus Fleet Charging Costs
The transition from diesel-powered buses to electric vehicles (EVs) presents a significant opportunity for public transportation operators to reduce operating expenses, improve environmental sustainability, and modernize fleet operations."*

## 5. External Knowledge Base & Web References

*No uncredited external reference matches detected.*

## 6. AI-Generation Signal Breakdown (Requirement 7)

| Component | Estimated Value | Interpretation |
| :--- | :---: | :--- |
| **RoBERTa Classifier (Supervised)** | 99.4% | Supervised synthetic classifier |
| **GPT-2 Perplexity (PPL)** | 19.62 | Lower PPL (<35) correlates with LLMs |
| **Sentence Burstiness (Length Variance)** | 18.60 | Lower burstiness (<35) indicates uniform machine cadence |
| **Composite AI Probability** | **99.6%** | Confidence: HIGH |

> [!NOTE]
> Probabilistic heuristic indicator. AI confidence alone never elevates risk to HIGH without corroborating external or peer matches.

## 7. Reviewer Rapid Decision Checklist (< 30 Seconds)

- [ ] Verify highlighted passages in Section 3/4 above against candidate submission.
- [ ] Confirm whether citation credit was omitted by author.
- [ ] **Action:** Initiate formal academic integrity escalation.