"""
Text similarity and distance metrics utility.
Computes lexical metrics (Jaccard token similarity, normalized Levenshtein distance)
to contrast with dense semantic vector similarity (e.g. for Scenario 2 paraphrase analysis).
"""

import re
from typing import Set

def tokenize_words(text: str) -> list[str]:
    """Tokenizes text into lowercase alphanumeric words."""
    return re.findall(r"\b\w+\b", text.lower())

def compute_jaccard_similarity(text_a: str, text_b: str) -> float:
    """
    Computes Jaccard similarity over word tokens:
    J(A, B) = |A ∩ B| / |A ∪ B|
    """
    words_a: Set[str] = set(tokenize_words(text_a))
    words_b: Set[str] = set(tokenize_words(text_b))
    
    if not words_a and not words_b:
        return 1.0
    if not words_a or not words_b:
        return 0.0
        
    intersection = len(words_a.intersection(words_b))
    union = len(words_a.union(words_b))
    return round(float(intersection) / float(union), 4)

def compute_levenshtein_distance(s1: str, s2: str) -> int:
    """Computes standard edit distance between two strings."""
    if len(s1) < len(s2):
        return compute_levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

def compute_normalized_levenshtein_similarity(s1: str, s2: str) -> float:
    """
    Computes normalized Levenshtein similarity:
    1 - (edit_distance / max(len(s1), len(s2)))
    """
    s1_clean = " ".join(s1.split())
    s2_clean = " ".join(s2.split())
    max_len = max(len(s1_clean), len(s2_clean))
    if max_len == 0:
        return 1.0
    dist = compute_levenshtein_distance(s1_clean, s2_clean)
    return round(1.0 - (dist / max_len), 4)

def format_timestamp(seconds: float) -> str:
    """Formats seconds into HH:MM:SS string."""
    s = max(0, int(round(seconds)))
    hrs = s // 3600
    mins = (s % 3600) // 60
    secs = s % 60
    return f"{hrs:02d}:{mins:02d}:{secs:02d}"

