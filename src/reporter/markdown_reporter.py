"""
Human-Readable Markdown Audit Report Generator.
Designed for evaluators and competition judges to cross-verify claims in under 30 seconds.
Includes side-by-side textual comparisons, semantic vs. lexical metrics, and boilerplate exclusions.
"""

from pathlib import Path
from typing import Dict, Any, List

def generate_markdown_report(
    doc_id: str,
    total_integrity_risk: str,
    peer_sim_pct: float,
    ext_sim_pct: float,
    ai_prob: float,
    peer_matches: List[Dict[str, Any]],
    multimodal_matches: List[Dict[str, Any]],
    external_matches: List[Dict[str, Any]],
    discounted_boilerplate: List[Dict[str, Any]],
    ai_signals: Dict[str, Any],
    explanations: str,
    status: str = "SUCCESS",
    warning_message: str = None
) -> str:
    """Generates comprehensive, formatted Markdown audit report."""
    risk_badges = {
        "HIGH": "🔴 HIGH INTEGRITY RISK",
        "MEDIUM": "🟡 MEDIUM INTEGRITY RISK",
        "LOW": "🟢 LOW INTEGRITY RISK (PASSED)",
        "FLAGGED": "⚠️ FLAGGED / DEGRADED FILE"
    }
    badge = risk_badges.get(total_integrity_risk, total_integrity_risk)

    md = []
    md.append(f"# Submission Integrity Audit: `{doc_id}`\n")
    md.append(f"**Overall Assessment:** **{badge}**\n")
    md.append(f"**System Recommendation:** {explanations}\n")

    if status != "SUCCESS":
        md.append(f"> [!WARNING]\n> **File Processing Status:** `{status}`\n> **Notice:** {warning_message}\n")

    # 1. Scores Summary
    md.append("## 1. Multi-Signal Integrity Scores\n")
    md.append("| Signal Metric | Score | Decision Boundary Threshold |")
    md.append("| :--- | :---: | :---: |")
    md.append(f"| **Internal Peer-to-Peer Similarity** | **{peer_sim_pct:.1f}%** | ≥ 50.0% (High), ≥ 20.0% (Medium) |")
    md.append(f"| **External / Reference Similarity** | **{ext_sim_pct:.1f}%** | ≥ 40.0% (High), ≥ 20.0% (Medium) |")
    md.append(f"| **AI-Generated Content Likelihood** | **{ai_prob:.1f}%** | Probabilistic (≥ 80.0% Medium alone) |")
    md.append("\n")

    # 2. Template / Boilerplate Discounting (Requirement 5)
    md.append("## 2. Template & Common Prompt Filtering (Scenario 4)\n")
    if discounted_boilerplate:
        md.append(f"The engine identified and **discounted {len(discounted_boilerplate)} chunk(s)** from plagiarism scoring to avoid penalizing shared case competition prompts:\n")
        md.append("| Discounted Snippet | Exclusion Reason | Cross-Doc Frequency |")
        md.append("| :--- | :--- | :---: |")
        for b in discounted_boilerplate:
            snippet = b.get("text_snippet", "").replace("\n", " ").replace("|", "-")
            reason = b.get("reason", "Institutional boilerplate")
            cnt = b.get("doc_count", 1)
            md.append(f"| *\"{snippet}\"* | {reason} | {cnt} docs |")
        md.append("\n")
    else:
        md.append("*No recurring institutional boilerplate or prompt templates required discounting for this file.*\n")

    # 3. Cross-Modal Matches (Scenario 1)
    md.append("## 3. Multimodal Audio/Video Cross-Matches (Scenario 1)\n")
    if multimodal_matches:
        md.append("Identified audio speech matching written submission passages:\n\n")
        for idx, m in enumerate(multimodal_matches, start=1):
            sim = m.get("similarity_score", 0.0)
            target = m.get("matched_file", "unknown")
            loc = m.get("location", {})
            q_loc = loc.get("query_timestamp") or f"Page {loc.get('query_page', '?')}"
            m_loc = loc.get("matched_timestamp") or f"Page {loc.get('matched_page', '?')}"
            
            md.append(f"### Match #{idx} — Target: `{target}` (Similarity: **{sim:.2f}**)")
            md.append(f"- **Query Location:** `{q_loc}`")
            md.append(f"- **Matched File Location:** `{m_loc}`")
            md.append(f"- **Offending Query Spoken/Text:**")
            md.append(f"  > *\"{m.get('query_passage', '')}\"*")
            md.append(f"- **Matched Counterpart:**")
            md.append(f"  > *\"{m.get('matched_passage', '')}\"*\n")
    else:
        md.append("*No cross-modal speech-to-text overlaps detected.*\n")

    # 4. Peer Text Matches (Scenario 2 Paraphrase Analysis)
    md.append("## 4. Internal Peer Document Overlaps & Paraphrasing (Scenario 2)\n")
    if peer_matches:
        for idx, m in enumerate(peer_matches, start=1):
            sim = m.get("similarity_score", 0.0)
            jaccard = m.get("lexical_jaccard", 0.0)
            lev = m.get("lexical_levenshtein", 0.0)
            is_para = m.get("is_paraphrase", False)
            target = m.get("matched_file", "unknown")
            loc = m.get("location", {})
            q_page = loc.get("query_page", 1)
            m_page = loc.get("matched_page", 1)

            para_note = " ⚠️ **[SYNONYM-BASED PARAPHRASE DETECTED]**" if is_para else ""
            md.append(f"### Overlap #{idx} — Target: `{target}`{para_note}")
            md.append("| Semantic Cosine Sim | Lexical Jaccard Sim | Levenshtein Sim | Page References |")
            md.append("| :---: | :---: | :---: | :---: |")
            md.append(f"| **{sim:.2f}** | **{jaccard:.2f}** | **{lev:.2f}** | Query: Pg {q_page} ↔ Match: Pg {m_page} |")
            if is_para:
                md.append("> **Reviewer Note:** High dense embedding similarity (>0.80) with low lexical Jaccard (<0.35) confirms semantic rewriting evasion.")
            md.append(f"- **Query Passage:**")
            md.append(f"  > *\"{m.get('query_passage', '')}\"*")
            md.append(f"- **Matched Source Passage:**")
            md.append(f"  > *\"{m.get('matched_passage', '')}\"*\n")
    else:
        md.append("*No internal peer document plagiarism detected.*\n")

    # 5. External Reference Matches
    md.append("## 5. External Knowledge Base & Web References\n")
    if external_matches:
        for idx, m in enumerate(external_matches, start=1):
            title = m.get("source_title", "External Article")
            url = m.get("source_url", "#")
            sim = m.get("similarity_score", 0.0)
            md.append(f"- **Source:** [{title}]({url}) (Cosine Sim: **{sim:.2f}**)")
            md.append(f"  - **Submission Text:** *\"{m.get('query_passage', '')}\"*")
            md.append(f"  - **Reference Text:** *\"{m.get('matched_passage', '')}\"*\n")
    else:
        md.append("*No uncredited external reference matches detected.*\n")

    # 6. AI Detection Analysis
    md.append("## 6. AI-Generation Signal Breakdown (Requirement 7)\n")
    if ai_signals:
        sig = ai_signals.get("signals", {})
        md.append("| Component | Estimated Value | Interpretation |")
        md.append("| :--- | :---: | :--- |")
        md.append(f"| **RoBERTa Classifier (Supervised)** | {sig.get('roberta_ai_prob', 0.0):.1f}% | Supervised synthetic classifier |")
        md.append(f"| **GPT-2 Perplexity (PPL)** | {sig.get('perplexity', 0.0):.2f} | Lower PPL (<35) correlates with LLMs |")
        md.append(f"| **Sentence Burstiness (Length Variance)** | {sig.get('burstiness', 0.0):.2f} | Lower burstiness (<35) indicates uniform machine cadence |")
        md.append(f"| **Composite AI Probability** | **{ai_prob:.1f}%** | Confidence: {ai_signals.get('confidence_level', 'N/A')} |")
        md.append(f"\n> [!NOTE]\n> {ai_signals.get('disclaimer', '')}\n")
    else:
        md.append("*AI detection skipped or not applicable.*\n")

    # 7. Verification Checklist (<30 seconds)
    md.append("## 7. Reviewer Rapid Decision Checklist (< 30 Seconds)\n")
    if total_integrity_risk == "HIGH":
        md.append("- [ ] Verify highlighted passages in Section 3/4 above against candidate submission.")
        md.append("- [ ] Confirm whether citation credit was omitted by author.")
        md.append("- [ ] **Action:** Initiate formal academic integrity escalation.")
    elif total_integrity_risk == "MEDIUM":
        md.append("- [ ] Check whether similarity is due to common domain definitions or LLM drafting assistance.")
        md.append("- [ ] **Action:** Request clarification from candidate or second reviewer inspection.")
    elif total_integrity_risk == "FLAGGED":
        md.append("- [ ] Candidate submitted an empty, corrupted, or silent media file.")
        md.append("- [ ] **Action:** Request file resubmission.")
    else:
        md.append("- [x] Originality verified. Low risk.")
        md.append("- [ ] **Action:** Fast-track to competition scoring.")

    return "\n".join(md)

def write_markdown_report(report_md: str, output_path: Path):
    """Writes Markdown report file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_md)
