"""
Text normalization and sentence splitting utilities.
Cleans raw extracted text, strips recurring headers/footers, and standardizes whitespace.
"""

import re
from typing import List

try:
    import nltk
    from nltk.tokenize import sent_tokenize
except ImportError:
    sent_tokenize = None

def clean_text(text: str) -> str:
    """
    Cleans raw text by stripping repetitive header/footer artifacts,
    unifying unicode quotes and dashes, and collapsing excessive whitespace.
    """
    if not text:
        return ""

    # Replace windows line endings
    cleaned = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove standard header/footer patterns: "Page X of Y", "Page X", "--- X ---"
    cleaned = re.sub(r"(?im)^\s*(page\s+\d+(\s+of\s+\d+)?|\d+\s*/\s*\d+|---\s*\d+\s*---)\s*$", "", cleaned)

    # Standardize curly quotes and special hyphens
    cleaned = cleaned.replace("“", '"').replace("”", '"').replace("’", "'").replace("‘", "'")
    cleaned = cleaned.replace("—", " - ").replace("–", " - ")

    # Reconstruct paragraphs from PDF line wraps:
    # 1. Join mid-sentence wraps (line ending without punctuation followed by lowercase or continuation)
    cleaned = re.sub(r"(?<![.!?:\n])\n(?=[a-z0-9])", " ", cleaned)
    # 2. Treat punctuation followed by newline and capitalized word as distinct paragraph break
    cleaned = re.sub(r"(?<=[.!?])\n(?=[A-Z0-9])", "\n\n", cleaned)

    # Collapse multiple blank lines to double newline
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    # Collapse repeated horizontal whitespace
    cleaned = re.sub(r"[ \t]+", " ", cleaned)

    return cleaned.strip()

def split_into_sentences(text: str) -> List[str]:
    """Splits a block of text into distinct sentences preserving punctuation."""
    cleaned = clean_text(text)
    if not cleaned:
        return []

    if sent_tokenize:
        try:
            raw_sents = sent_tokenize(cleaned)
            # Filter trivial noise
            return [s.strip() for s in raw_sents if len(s.strip()) > 3]
        except Exception:
            pass

    # Fallback sentence tokenizer regex
    sentence_regex = r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s"
    sentences = re.split(sentence_regex, cleaned)
    return [s.strip() for s in sentences if len(s.strip()) > 3]
