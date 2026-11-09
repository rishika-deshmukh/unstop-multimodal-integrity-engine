"""
Batch evaluation summary generator.
Computes aggregate corpus statistics, top offenders,
and pairwise document similarity matrix (CSV + Markdown heatmap table).
"""

from typing import List, Dict, Any
from pathlib import Path
import csv
import numpy as np

def generate_summary_matrix(
    doc_ids: List[str],
    pairwise_matrix: np.ndarray,
    reports_map: Dict[str, Dict[str, Any]],
    output_dir: Path
):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Export CSV Pairwise Similarity Matrix
    csv_path = output_dir / "summary_matrix.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["document_id"] + doc_ids)
        for i, doc_a in enumerate(doc_ids):
            row = [doc_a] + [f"{pairwise_matrix[i, j]:.2f}" for j in range(len(doc_ids))]
            writer.writerow(row)

    # 2. Export Markdown Summary Report with Heatmap Table
    md_path = output_dir / "batch_summary_report.md"
    md = []
    md.append("# Batch Integrity Evaluation Summary\n")
    md.append(f"**Total Submissions Evaluated:** {len(doc_ids)}\n")

    # Risk tally
    risk_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "FLAGGED": 0}
    for doc_id, r in reports_map.items():
        risk = r.get("total_integrity_risk", "LOW")
        risk_counts[risk] = risk_counts.get(risk, 0) + 1

    md.append("## 1. Risk Distribution Overview\n")
    md.append("| Risk Classification | Count | Percentage |")
    md.append("| :--- | :---: | :---: |")
    n_total = max(1, len(doc_ids))
    md.append(f"| 🔴 **HIGH RISK** | {risk_counts.get('HIGH', 0)} | {(risk_counts.get('HIGH', 0)/n_total)*100:.1f}% |")
    md.append(f"| 🟡 **MEDIUM RISK** | {risk_counts.get('MEDIUM', 0)} | {(risk_counts.get('MEDIUM', 0)/n_total)*100:.1f}% |")
    md.append(f"| 🟢 **LOW RISK (Passed)** | {risk_counts.get('LOW', 0)} | {(risk_counts.get('LOW', 0)/n_total)*100:.1f}% |")
    md.append(f"| ⚠️ **FLAGGED / DEGRADED** | {risk_counts.get('FLAGGED', 0)} | {(risk_counts.get('FLAGGED', 0)/n_total)*100:.1f}% |")
    md.append("\n")

    # Submission Leaderboard
    md.append("## 2. Submission Results Table\n")
    md.append("| Document ID | Risk Category | Peer % | External % | AI Prob % | Status |")
    md.append("| :--- | :---: | :---: | :---: | :---: | :--- |")
    for doc_id in doc_ids:
        r = reports_map.get(doc_id, {})
        scores = r.get("scores", {})
        risk = r.get("total_integrity_risk", "LOW")
        badge = {"HIGH": "🔴 HIGH", "MEDIUM": "🟡 MEDIUM", "LOW": "🟢 LOW", "FLAGGED": "⚠️ FLAGGED"}.get(risk, risk)
        p_pct = scores.get("peer_similarity_percentage", 0.0)
        e_pct = scores.get("external_similarity_percentage", 0.0)
        ai_p = scores.get("ai_generated_probability", 0.0)
        stat = r.get("status", "SUCCESS")
        md.append(f"| `{doc_id}` | {badge} | {p_pct:.1f}% | {e_pct:.1f}% | {ai_p:.1f}% | `{stat}` |")
    md.append("\n")

    # Heatmap Table
    md.append("## 3. Pairwise Cross-Document Similarity Matrix\n")
    md.append("*Values represent max semantic overlap between document chunk vectors (excluding self-matches).*\n")
    
    # Shorten doc names for table column headers
    short_names = [f"D{i+1}" for i in range(len(doc_ids))]
    legend_str = ", ".join([f"**D{i+1}**: `{d}`" for i, d in enumerate(doc_ids)])
    md.append(f"> **Legend:** {legend_str}\n")

    header_cols = ["Doc"] + short_names
    md.append("| " + " | ".join(header_cols) + " |")
    md.append("| " + " | ".join([":---:"] * len(header_cols)) + " |")

    for i, doc_a in enumerate(doc_ids):
        row_vals = [f"**D{i+1}**"]
        for j in range(len(doc_ids)):
            val = pairwise_matrix[i, j]
            if i == j:
                row_vals.append("—")
            elif val >= 0.80:
                row_vals.append(f"**`{val:.2f}`** 🔴")
            elif val >= 0.60:
                row_vals.append(f"`{val:.2f}` 🟡")
            else:
                row_vals.append(f"{val:.2f}")
        md.append("| " + " | ".join(row_vals) + " |")

    md.append("\n")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
