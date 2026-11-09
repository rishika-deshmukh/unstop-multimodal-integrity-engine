"""
Multi-signal AI-Generated Content Estimation Module.
Combines a calibrated RoBERTa classification model (roberta-base-openai-detector)
with GPT-2 token perplexity and sentence burstiness heuristics.
"""

import math
import logging
from typing import Dict, Any, List
import numpy as np
import torch
import torch.nn.functional as F
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    GPT2LMHeadModel,
    GPT2TokenizerFast
)

from src.normalizer.normalizer import clean_text, split_into_sentences

logger = logging.getLogger("ai_detector")

class AIDetector:
    def __init__(
        self,
        classifier_model: str = "roberta-base-openai-detector",
        gpt2_model: str = "gpt2",
        device: str = "cpu"
    ):
        self.classifier_name = classifier_model
        self.gpt2_name = gpt2_model
        self.device = device

        self._clf_tokenizer = None
        self._clf_model = None
        self._gpt2_tokenizer = None
        self._gpt2_model = None

    def _load_classifier(self):
        if self._clf_model is None:
            logger.info(f"Loading AI classifier '{self.classifier_name}' on {self.device}...")
            self._clf_tokenizer = AutoTokenizer.from_pretrained(self.classifier_name)
            self._clf_model = AutoModelForSequenceClassification.from_pretrained(self.classifier_name)
            self._clf_model.to(self.device)
            self._clf_model.eval()

    def _load_gpt2(self):
        if self._gpt2_model is None:
            logger.info(f"Loading GPT-2 model '{self.gpt2_name}' for perplexity on {self.device}...")
            self._gpt2_tokenizer = GPT2TokenizerFast.from_pretrained(self.gpt2_name)
            self._gpt2_model = GPT2LMHeadModel.from_pretrained(self.gpt2_name)
            self._gpt2_model.to(self.device)
            self._gpt2_model.eval()

    def compute_roberta_ai_prob(self, text: str) -> float:
        """Runs supervised AI detector with dynamic id2label mapping."""
        self._load_classifier()
        # Truncate to 512 tokens
        inputs = self._clf_tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512
        ).to(self.device)

        with torch.no_grad():
            outputs = self._clf_model(**inputs)
            probs = F.softmax(outputs.logits, dim=-1)[0]
            
            # Dynamically resolve index for AI / Fake / ChatGPT class
            ai_idx = 0
            if hasattr(self._clf_model.config, "id2label") and self._clf_model.config.id2label:
                for idx, lbl in self._clf_model.config.id2label.items():
                    if any(w in lbl.lower() for w in ("fake", "chatgpt", "ai", "machine")):
                        ai_idx = int(idx)
                        break

            ai_prob = float(probs[ai_idx].item()) * 100.0
            return round(ai_prob, 2)

    def compute_perplexity(self, text: str) -> float:
        """Computes GPT-2 token perplexity: exp(cross_entropy_loss)."""
        self._load_gpt2()
        encodings = self._gpt2_tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=1024
        ).to(self.device)

        input_ids = encodings.input_ids
        if input_ids.size(1) < 5:
            return 100.0  # Default neutral perplexity for very short text

        with torch.no_grad():
            outputs = self._gpt2_model(input_ids, labels=input_ids)
            loss = outputs.loss
            ppl = math.exp(loss.item())
            return round(min(ppl, 999.0), 2)

    def compute_burstiness(self, text: str) -> float:
        """
        Computes sentence-length variance (burstiness).
        Human text exhibits high burstiness (mixing short & long sentences).
        AI text exhibits uniform, low-variance sentence structures.
        """
        sentences = split_into_sentences(text)
        if len(sentences) < 3:
            return 50.0  # Neutral burstiness for sparse text

        lengths = [len(s.split()) for s in sentences]
        variance = float(np.var(lengths))
        mean = float(np.mean(lengths)) if np.mean(lengths) > 0 else 1.0

        # Coefficient of variation (std / mean)
        cv = (np.sqrt(variance) / mean)
        # Scaled burstiness score: higher CV -> higher human burstiness (0-100)
        burstiness_score = round(float(np.clip(cv * 60.0, 0.0, 100.0)), 2)
        return burstiness_score

    def analyze(self, raw_text: str) -> Dict[str, Any]:
        """
        Multi-signal analysis combining RoBERTa classifier, perplexity, and burstiness.
        Returns composite probability and signal breakdown.
        """
        text = clean_text(raw_text)
        if not text or len(text.split()) < 20:
            return {
                "ai_generated_probability": 0.0,
                "confidence_level": "INSUFFICIENT_TEXT",
                "signals": {
                    "roberta_ai_prob": 0.0,
                    "perplexity": 0.0,
                    "burstiness": 0.0
                },
                "disclaimer": "Text length under 20 words is insufficient for statistical AI detection."
            }

        try:
            roberta_score = self.compute_roberta_ai_prob(text)
        except Exception as e:
            logger.warning(f"RoBERTa detection failed: {e}. Falling back to statistical heuristics.")
            roberta_score = 50.0

        try:
            ppl = self.compute_perplexity(text)
        except Exception as e:
            logger.warning(f"Perplexity computation failed: {e}")
            ppl = 45.0

        try:
            burstiness = self.compute_burstiness(text)
        except Exception as e:
            burstiness = 50.0

        # Heuristic calibration:
        # Low perplexity (<30) + Low burstiness (<30) indicates synthetic generation
        # High perplexity (>60) + High burstiness (>50) indicates human variance
        ppl_ai_indicator = float(np.clip((60.0 - ppl) / 40.0 * 100.0, 0.0, 100.0))
        burst_ai_indicator = float(np.clip((60.0 - burstiness) / 40.0 * 100.0, 0.0, 100.0))

        # Composite weighting: 65% RoBERTa + 20% Perplexity + 15% Burstiness
        composite = 0.65 * roberta_score + 0.20 * ppl_ai_indicator + 0.15 * burst_ai_indicator
        composite_score = round(float(np.clip(composite, 0.0, 100.0)), 1)

        confidence = "HIGH" if composite_score > 75.0 or composite_score < 25.0 else "MODERATE"

        return {
            "ai_generated_probability": composite_score,
            "confidence_level": confidence,
            "signals": {
                "roberta_ai_prob": roberta_score,
                "perplexity": ppl,
                "burstiness": burstiness
            },
            "disclaimer": "Probabilistic heuristic indicator. AI confidence alone never elevates risk to HIGH without corroborating external or peer matches."
        }
