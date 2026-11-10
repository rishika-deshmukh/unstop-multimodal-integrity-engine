"""
Comprehensive Unit Test Suite for Multimodal Integrity & Plagiarism Engine.
Tests all extractors, edge cases (corrupt/empty/silent files), vector indexing,
boilerplate filtering, and multi-signal scoring.
"""

import os
import sys
import json
from pathlib import Path
import pytest
import numpy as np

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.extractors.pdf_extractor import PDFExtractor
from src.extractors.docx_extractor import DOCXExtractor
from src.extractors.video_extractor import VideoExtractor
from src.extractors.dispatcher import DocumentParser
from src.normalizer.normalizer import clean_text, split_into_sentences
from src.normalizer.chunker import DocumentChunker, DocumentChunk
from src.filters.boilerplate_filter import BoilerplateFilter
from src.indexer.vector_indexer import VectorIndexer
from src.utils.text_metrics import compute_jaccard_similarity, compute_normalized_levenshtein_similarity
from src.detectors.risk_calculator import RiskCalculator

SAMPLE_DIR = Path("./sample_submissions")

def test_pdf_extractor_valid_and_zero_byte():
    extractor = PDFExtractor()
    
    # 1. Zero-byte PDF (Scenario 3)
    p_zero = SAMPLE_DIR / "submission_06_corrupt_empty.pdf"
    doc_zero = extractor.extract(p_zero)
    assert doc_zero.status == "SKIPPED_EMPTY"
    assert not doc_zero.is_usable
    assert "Zero-byte" in (doc_zero.warning_message or "")

    # 2. Valid PDF
    p_valid = SAMPLE_DIR / "submission_01_fintech_report.pdf"
    doc_valid = extractor.extract(p_valid)
    assert doc_valid.status == "SUCCESS"
    assert doc_valid.is_usable
    assert len(doc_valid.pages) >= 2
    assert "vertical integration" in doc_valid.raw_text.lower()

def test_docx_extractor_valid_and_corrupt():
    extractor = DOCXExtractor()

    # 1. Corrupt DOCX (Scenario 3)
    p_corrupt = SAMPLE_DIR / "submission_08_corrupted.docx"
    doc_corrupt = extractor.extract(p_corrupt)
    assert doc_corrupt.status == "SKIPPED_CORRUPT"
    assert not doc_corrupt.is_usable
    assert "Corrupt" in (doc_corrupt.warning_message or "")

    # 2. Valid DOCX
    p_valid = SAMPLE_DIR / "submission_03_logistics_strategy.docx"
    doc_valid = extractor.extract(p_valid)
    assert doc_valid.status == "SUCCESS"
    assert doc_valid.is_usable
    assert "cold chain" in doc_valid.raw_text.lower()

def test_video_extractor_silent_handling():
    # Silent MP4 (Scenario 3)
    extractor = VideoExtractor(model_name="openai/whisper-tiny", device="cpu")
    p_silent = SAMPLE_DIR / "submission_07_silent_video.mp4"
    doc_silent = extractor.extract(p_silent)
    assert doc_silent.status == "SKIPPED_SILENT"
    assert not doc_silent.is_usable

def test_lexical_vs_semantic_paraphrasing():
    # Scenario 2 Paraphrase Test: Semantic > 0.80 while Lexical is low
    text_orig = (
        "Establishing a resilient pharmaceutical cold chain requires continuous thermal monitoring "
        "between two and eight degrees Celsius across all intermediate warehouse hubs. Active refrigeration "
        "containers utilizing automated compressor cycles guarantee temperature stability during transcontinental "
        "flights, whereas passive thermal shippers rely on vacuum-insulated panels to protect vaccines during domestic road haulage."
    )
    text_para = (
        "Constructing a dependable pharmaceutical thermal supply line demands nonstop temperature tracking "
        "between two and eight degrees Celsius across every midpoint depot location. Active refrigerated "
        "enclosures deploying computerized cooling mechanisms ensure temperature consistency during international "
        "flight segments, while passive temperature-safe boxes depend on vacuum-insulated panels to safeguard vaccine vials throughout ground truck transport."
    )

    # Lexical Jaccard should be low due to synonym replacement (< 0.40)
    jaccard = compute_jaccard_similarity(text_orig, text_para)
    assert jaccard < 0.40, f"Expected low Jaccard (<0.40) but got {jaccard}"

    # Semantic embedding similarity should be high (>= 0.80)
    indexer = VectorIndexer(model_name="all-MiniLM-L6-v2", device="cpu")
    embs = indexer.embed_texts([text_orig, text_para])
    cosine_sim = float(np.dot(embs[0], embs[1]))
    assert cosine_sim >= 0.80, f"Expected high cosine similarity (>=0.80) but got {cosine_sim}"

def test_boilerplate_filtering_scenario_4():
    # Scenario 4: Chunks occurring in >= 3 docs should be marked as boilerplate
    bp_filter = BoilerplateFilter(min_doc_frequency=3, similarity_threshold=0.88, short_chunk_word_limit=15)
    prompt_text = (
        "Case Study Challenge Brief 2026: Sustainable Urban Mobility Infrastructure. "
        "Teams are required to evaluate the capital deployment feasibility and regulatory constraints "
        "of transitioning municipal transit networks to zero-emission battery electric bus fleets."
    )

    chunks = [
        DocumentChunk("d1#c1", "doc1", "doc1.pdf", "pdf", prompt_text, word_count=28),
        DocumentChunk("d2#c1", "doc2", "doc2.pdf", "pdf", prompt_text, word_count=28),
        DocumentChunk("d3#c1", "doc3", "doc3.pdf", "pdf", prompt_text, word_count=28),
        DocumentChunk("d1#c2", "doc1", "doc1.pdf", "pdf", "Completely unique original analysis for doc1.", word_count=20),
        DocumentChunk("d2#c2", "doc2", "doc2.pdf", "pdf", "Completely unique original analysis for doc2.", word_count=20),
    ]

    indexer = VectorIndexer(model_name="all-MiniLM-L6-v2", device="cpu")
    embs = indexer.embed_texts([c.text for c in chunks])
    filtered_chunks = bp_filter.identify_and_filter(chunks, embs)

    # The 3 prompt chunks must be marked as boilerplate
    assert filtered_chunks[0].is_boilerplate is True
    assert filtered_chunks[1].is_boilerplate is True
    assert filtered_chunks[2].is_boilerplate is True
    # The unique analysis chunks must NOT be marked as boilerplate
    assert filtered_chunks[3].is_boilerplate is False
    assert filtered_chunks[4].is_boilerplate is False

def test_vector_indexer_self_exclusion():
    # Requirement 6: Exclusion by doc_id
    indexer = VectorIndexer(model_name="all-MiniLM-L6-v2", device="cpu")
    chunk_a = DocumentChunk("doc1#c1", "doc1", "doc1.pdf", "pdf", "Machine learning transforms automated underwriting.")
    chunk_b = DocumentChunk("doc1#c2", "doc1", "doc1.pdf", "pdf", "Machine learning transforms automated underwriting.") # Duplicate inside same doc
    chunk_c = DocumentChunk("doc2#c1", "doc2", "doc2.pdf", "pdf", "Machine learning transforms automated underwriting.") # Peer doc

    chunks = [chunk_a, chunk_b, chunk_c]
    embs = indexer.embed_texts([c.text for c in chunks])
    indexer.index_chunks(chunks, embs)

    # Searching with chunk_a should NEVER return chunk_a or chunk_b (same doc_id), only chunk_c
    matches = indexer.search_matches_for_chunk(chunk_a, embs[0], top_k=5, min_similarity=0.80)
    matched_doc_ids = [m.matched_chunk.doc_id for m in matches]
    assert "doc1" not in matched_doc_ids
    assert "doc2" in matched_doc_ids

def test_risk_calculator_ai_never_triggers_high_alone():
    # Requirement 7 & 9: AI probability alone must never trigger HIGH risk
    config = {
        "risk_thresholds": {
            "high": {"peer_min": 50.0, "external_min": 40.0, "combined_peer_and_ai": {"peer_min": 30.0, "ai_min": 70.0}},
            "medium": {"peer_min": 20.0, "external_min": 20.0, "ai_min_with_peer": {"peer_min": 10.0, "ai_min": 70.0}, "ai_standalone_min": 80.0}
        }
    }
    rc = RiskCalculator(config)

    # High AI (95%), but zero peer and zero external
    risk, _ = rc.calculate_risk(peer_pct=0.0, external_pct=0.0, ai_prob=95.0)
    assert risk == "MEDIUM", f"Expected MEDIUM but got {risk} (AI alone must never trigger HIGH)"

    # High Peer (65%), low AI (10%)
    risk_high, _ = rc.calculate_risk(peer_pct=65.0, external_pct=0.0, ai_prob=10.0)
    assert risk_high == "HIGH"

def test_cross_modal_match_page_and_timestamp():
    # Scenario 1: Video speech transcription matching PDF page and timestamp
    report_path = Path("./reports/submission_02_video_pitch.mp4.json")
    assert report_path.exists(), f"Report file {report_path} must exist from run_integrity_check.py"
    with open(report_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    assert data["total_integrity_risk"] == "HIGH"
    assert data["scores"]["peer_similarity_percentage"] == 100.0
    assert len(data["multimodal_matches"]) >= 1
    
    match = data["multimodal_matches"][0]
    assert match["matched_file"] == "submission_01_fintech_report.pdf"
    assert match["location"]["matched_page"] == 2
    assert match["location"]["query_timestamp"] is not None
    assert "00:00:" in match["location"]["query_timestamp"]
    assert match["similarity_score"] >= 0.80

def test_external_match_submission_18():
    # Scenario 5: External knowledge base plagiarism detection
    report_path = Path("./reports/submission_18_external_plagiarism.pdf.json")
    assert report_path.exists(), f"Report file {report_path} must exist from run_integrity_check.py"
    with open(report_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    assert data["total_integrity_risk"] == "HIGH"
    assert data["scores"]["external_similarity_percentage"] >= 40.0
    assert "external source matching" in data["explanations"].lower()

