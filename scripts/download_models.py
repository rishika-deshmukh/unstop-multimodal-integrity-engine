"""
Model Downloader & Cache Warm-Up Script
Pre-fetches and caches all required open-source models:
1. SentenceTransformers: all-MiniLM-L6-v2 (for dense vector embedding)
2. OpenAI Whisper: tiny / base (for audio ASR)
3. GPT-2: for perplexity & burstiness statistical computation
4. RoBERTa AI Detector: for supervised AI-generated text classification
"""

import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("model_downloader")

def warm_up():
    logger.info("Initializing model pre-caching...")

    # 1. Sentence-Transformers
    try:
        from sentence_transformers import SentenceTransformer
        logger.info("Downloading SentenceTransformer 'all-MiniLM-L6-v2'...")
        _ = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("SentenceTransformer 'all-MiniLM-L6-v2' cached successfully.")
    except Exception as e:
        logger.error(f"Failed to cache SentenceTransformer: {e}")

    # 2. Whisper
    try:
        import whisper
        logger.info("Downloading Whisper 'base'...")
        _ = whisper.load_model("base")
        logger.info("Whisper 'base' cached successfully.")
    except Exception as e:
        logger.error(f"Failed to cache Whisper: {e}")

    # 3. GPT-2 for Perplexity & Burstiness
    try:
        from transformers import GPT2LMHeadModel, GPT2TokenizerFast
        logger.info("Downloading GPT-2 for Perplexity & Burstiness analysis...")
        _ = GPT2TokenizerFast.from_pretrained("gpt2")
        _ = GPT2LMHeadModel.from_pretrained("gpt2")
        logger.info("GPT-2 cached successfully.")
    except Exception as e:
        logger.error(f"Failed to cache GPT-2: {e}")

    # 4. RoBERTa AI Detector
    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        logger.info("Downloading RoBERTa AI detector ('roberta-base-openai-detector')...")
        model_name = "roberta-base-openai-detector"
        _ = AutoTokenizer.from_pretrained(model_name)
        _ = AutoModelForSequenceClassification.from_pretrained(model_name)
        logger.info("RoBERTa AI detector cached successfully.")
    except Exception as e:
        logger.warning(f"Could not download primary detector ({e}). Trying fallback...")
        try:
            fallback = "Hello-SimpleAI/chatgpt-detector-roberta"
            _ = AutoTokenizer.from_pretrained(fallback)
            _ = AutoModelForSequenceClassification.from_pretrained(fallback)
            logger.info("Fallback AI detector cached successfully.")
        except Exception as e2:
            logger.error(f"Fallback detector download failed: {e2}")

    logger.info("Model download and cache warm-up process complete.")

if __name__ == "__main__":
    warm_up()
