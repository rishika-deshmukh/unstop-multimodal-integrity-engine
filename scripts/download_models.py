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

    # 2. Whisper (Transformers pipeline using openai/whisper-tiny)
    try:
        from transformers import pipeline
        logger.info("Downloading Whisper 'openai/whisper-tiny'...")
        _ = pipeline("automatic-speech-recognition", model="openai/whisper-tiny", chunk_length_s=30)
        logger.info("Whisper 'openai/whisper-tiny' cached successfully.")
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

    # 4. RoBERTa AI Detector (Primary model from config.yaml: Hello-SimpleAI/chatgpt-detector-roberta)
    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        model_name = "Hello-SimpleAI/chatgpt-detector-roberta"
        logger.info(f"Downloading primary AI detector ('{model_name}')...")
        _ = AutoTokenizer.from_pretrained(model_name)
        _ = AutoModelForSequenceClassification.from_pretrained(model_name)
        logger.info(f"Primary AI detector '{model_name}' cached successfully.")
    except Exception as e:
        logger.error(f"Failed to cache primary AI detector: {e}")

    # Optional benchmark detector (roberta-base-openai-detector)
    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        bm_name = "roberta-base-openai-detector"
        logger.info(f"Downloading benchmark AI detector ('{bm_name}')...")
        _ = AutoTokenizer.from_pretrained(bm_name)
        _ = AutoModelForSequenceClassification.from_pretrained(bm_name)
        logger.info(f"Benchmark AI detector '{bm_name}' cached successfully.")
    except Exception as e:
        logger.warning(f"Could not cache secondary benchmark detector: {e}")

    logger.info("Model download and cache warm-up process complete.")

if __name__ == "__main__":
    warm_up()
