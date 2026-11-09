"""
Integrity Risk Evaluation Module.
Implements multi-signal decision logic mapping Peer, External, and AI scores
to LOW / MEDIUM / HIGH categories according to config.yaml rules.
"""

from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger("risk_calculator")

class RiskCalculator:
    def __init__(self, config: Dict[str, Any]):
        self.risk_cfg = config.get("risk_thresholds", {})
        self.high_cfg = self.risk_cfg.get("high", {})
        self.med_cfg = self.risk_cfg.get("medium", {})

    def calculate_risk(
        self,
        peer_pct: float,
        external_pct: float,
        ai_prob: float
    ) -> Tuple[str, str]:
        """
        Determines total integrity risk category and generates concise human explanation.
        Guarantees that AI-generation probability alone never triggers HIGH risk.
        """
        # 1. HIGH RISK EVALUATION
        high_peer_min = self.high_cfg.get("peer_min", 50.0)
        high_ext_min = self.high_cfg.get("external_min", 40.0)
        comb_high = self.high_cfg.get("combined_peer_and_ai", {})
        comb_peer_min = comb_high.get("peer_min", 30.0)
        comb_ai_min = comb_high.get("ai_min", 70.0)

        if peer_pct >= high_peer_min:
            return "HIGH", f"Critical internal peer similarity detected ({peer_pct}% exceeds {high_peer_min}% threshold)."

        if external_pct >= high_ext_min:
            return "HIGH", f"Extensive uncredited external source matching detected ({external_pct}% exceeds {high_ext_min}% threshold)."

        if peer_pct >= comb_peer_min and ai_prob >= comb_ai_min:
            return "HIGH", (
                f"High integrity risk: Significant peer duplication ({peer_pct}%) compounded by elevated AI-generation probability ({ai_prob}%)."
            )

        # 2. MEDIUM RISK EVALUATION
        med_peer_min = self.med_cfg.get("peer_min", 20.0)
        med_ext_min = self.med_cfg.get("external_min", 20.0)
        comb_med = self.med_cfg.get("ai_min_with_peer", {})
        comb_med_peer_min = comb_med.get("peer_min", 10.0)
        comb_med_ai_min = comb_med.get("ai_min", 70.0)
        standalone_ai_min = self.med_cfg.get("ai_standalone_min", 80.0)

        if peer_pct >= med_peer_min:
            return "MEDIUM", f"Moderate peer overlap detected ({peer_pct}% exceeds {med_peer_min}% threshold)."

        if external_pct >= med_ext_min:
            return "MEDIUM", f"Moderate external reference match detected ({external_pct}% exceeds {med_ext_min}% threshold)."

        if peer_pct >= comb_med_peer_min and ai_prob >= comb_med_ai_min:
            return "MEDIUM", f"Moderate overlap ({peer_pct}%) accompanied by AI-generated probability ({ai_prob}%)."

        if ai_prob >= standalone_ai_min:
            return "MEDIUM", (
                f"Elevated AI-generated content probability ({ai_prob}%). Categorized as MEDIUM risk pending human review; AI indicator alone does not trigger HIGH."
            )

        # 3. LOW RISK
        return "LOW", "Document integrity verified. Minimal similarity overlap and acceptable originality metrics."
