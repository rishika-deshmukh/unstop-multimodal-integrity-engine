"""
Configuration loader utility.
Reads and validates config.yaml parameters with fallback defaults.
"""

import os
import yaml
import logging
from typing import Any, Dict

logger = logging.getLogger("config_loader")

DEFAULT_CONFIG: Dict[str, Any] = {
    "models": {
        "embedding_model": "all-MiniLM-L6-v2",
        "whisper_model": "base",
        "ai_detector_model": "roberta-base-openai-detector",
        "gpt2_model": "gpt2",
        "device": "cpu",
    },
    "chunking": {
        "chunk_size_tokens": 250,
        "chunk_overlap_tokens": 50,
        "min_chunk_words": 15,
    },
    "boilerplate_filter": {
        "enabled": True,
        "min_doc_frequency": 3,
        "similarity_threshold": 0.90,
        "short_chunk_word_limit": 15,
    },
    "similarity": {
        "chunk_match_threshold": 0.80,
        "sentence_alignment_threshold": 0.75,
        "lexical_jaccard_low_threshold": 0.35,
    },
    "risk_thresholds": {
        "high": {
            "peer_min": 50.0,
            "external_min": 40.0,
            "combined_peer_and_ai": {
                "peer_min": 30.0,
                "ai_min": 70.0,
            },
        },
        "medium": {
            "peer_min": 20.0,
            "external_min": 20.0,
            "ai_min_with_peer": {
                "peer_min": 10.0,
                "ai_min": 70.0,
            },
            "ai_standalone_min": 80.0,
        },
    },
    "paths": {
        "external_kb_dir": "./external_kb",
        "reports_dir": "./reports",
    },
}

def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Loads configuration from YAML file or returns default."""
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                user_cfg = yaml.safe_load(f)
                if isinstance(user_cfg, dict):
                    # Deep merge with defaults
                    merged = DEFAULT_CONFIG.copy()
                    for k, v in user_cfg.items():
                        if isinstance(v, dict) and k in merged and isinstance(merged[k], dict):
                            merged[k] = {**merged[k], **v}
                        else:
                            merged[k] = v
                    return merged
        except Exception as e:
            logger.warning(f"Error parsing {config_path}: {e}. Using defaults.")
    return DEFAULT_CONFIG
