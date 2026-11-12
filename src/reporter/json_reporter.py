"""
JSON Audit Report Generator.
Strictly adheres to the specification standard on Pages 5-6 of the assessment brief.
"""

import json
from pathlib import Path
from typing import Dict, Any, List

def format_json_report(
    doc_id: str,
    total_integrity_risk: str,
    peer_sim_pct: float,
    ext_sim_pct: float,
    ai_prob: float,
    peer_matches: List[Dict[str, Any]],
    multimodal_matches: List[Dict[str, Any]],
    explanations: str,
    external_matches: List[Dict[str, Any]] = None,
    status: str = "SUCCESS",
    warning_message: str = None
) -> Dict[str, Any]:
    """Builds dictionary conforming strictly to assessment JSON schema."""
    report = {
        "document_id": doc_id,
        "total_integrity_risk": total_integrity_risk,
        "scores": {
            "peer_similarity_percentage": round(peer_sim_pct, 1),
            "external_similarity_percentage": round(ext_sim_pct, 1),
            "ai_generated_probability": round(ai_prob, 1)
        },
        "peer_matches": peer_matches,
        "multimodal_matches": multimodal_matches,
        "external_matches": external_matches or [],
        "explanations": explanations
    }

    if status != "SUCCESS":
        report["status"] = status
        if warning_message:
            report["warning"] = warning_message

    return report

def write_json_report(report_data: Dict[str, Any], output_path: Path):
    """Writes JSON report file with clean 2-space indentation."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
