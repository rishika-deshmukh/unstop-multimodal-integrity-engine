"""
Model Downloader & Cache Warm-Up Script
Pre-fetches and caches all required open-source models configured in config.yaml:
1. SentenceTransformers: all-MiniLM-L6-v2 (for dense vector embedding)
2. Hugging Face Whisper: openai/whisper-tiny (for audio ASR)
3. GPT-2: for perplexity & burstiness statistical computation
4. RoBERTa AI Detector: Hello-SimpleAI/chatgpt-detector-roberta (for supervised AI classification)
"""

import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("model_downloader")

def warm_up():
    logger.info("Initializing model pre-caching matching config.yaml...")

    # 1. Sentence-Transformers
    try:
        from sentence_transformers import SentenceTransformer
        logger.info("Downloading SentenceTransformer 'all-MiniLM-L6-v2'...")
        _ = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("SentenceTransformer 'all-MiniLM-L6-v2' cached successfully.")
    except Exception as e:
        logger.error(f"Failed to cache SentenceTransformer: {e}")

    # 2. Whisper ASR (Hugging Face Transformers)
    try:
        from transformers import WhisperProcessor, WhisperForConditionalGeneration
        logger.info("Downloading Hugging Face Whisper 'openai/whisper-tiny'...")
        _ = WhisperProcessor.from_pretrained("openai/whisper-tiny")
        _ = WhisperForConditionalGeneration.from_pretrained("openai/whisper-tiny")
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

    # 4. RoBERTa AI Detector (Hello-SimpleAI/chatgpt-detector-roberta)
    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        logger.info("Downloading AI detector 'Hello-SimpleAI/chatgpt-detector-roberta'...")
        model_name = "Hello-SimpleAI/chatgpt-detector-roberta"
        _ = AutoTokenizer.from_pretrained(model_name)
        _ = AutoModelForSequenceClassification.from_pretrained(model_name)
        logger.info("AI detector 'Hello-SimpleAI/chatgpt-detector-roberta' cached successfully.")
    except Exception as e:
        logger.error(f"Failed to cache AI detector: {e}")

    logger.info("Model download and cache warm-up process complete.")

if __name__ == "__main__":
    warm_up()
