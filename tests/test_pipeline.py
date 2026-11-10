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

def test_boilerplate_does_not_excuse_body_collusion():
    # Hard Requirement: 4 colluding students copying a body paragraph in a 15-doc cohort (26.7%)
    # must NOT be excused as institutional boilerplate (eliminates the prevalence loophole).
    bp_filter = BoilerplateFilter(min_doc_frequency=3, similarity_threshold=0.88, short_chunk_word_limit=15)
    copied_body_text = (
        "In our empirical assessment of municipal bus route electrification, we determine that "
        "peak fleet charging demands necessitate dedicated substation interconnects to mitigate "
        "transformer thermal stress during concurrent evening depot replenishment cycles."
    )

    # 15 documents in cohort
    chunks = []
    # 4 colluding students (docs 1-4) copying a substantive body paragraph (chunk_index == 2)
    for i in range(1, 5):
        chunks.append(DocumentChunk(f"doc{i}#c0", f"doc{i}", f"doc{i}.pdf", "pdf", f"Unique document title {i}.", word_count=18, chunk_index=0))
        chunks.append(DocumentChunk(f"doc{i}#c1", f"doc{i}", f"doc{i}.pdf", "pdf", f"Unique intro {i} outlining urban mobility context.", word_count=20, chunk_index=1))
        chunks.append(DocumentChunk(f"doc{i}#c2", f"doc{i}", f"doc{i}.pdf", "pdf", copied_body_text, word_count=35, chunk_index=2))

    # Remaining 11 benign students (docs 5-15)
    for i in range(5, 16):
        chunks.append(DocumentChunk(f"doc{i}#c0", f"doc{i}", f"doc{i}.pdf", "pdf", f"Unique document title {i}.", word_count=18, chunk_index=0))
        chunks.append(DocumentChunk(f"doc{i}#c1", f"doc{i}", f"doc{i}.pdf", "pdf", f"Unique intro {i}.", word_count=20, chunk_index=1))
        chunks.append(DocumentChunk(f"doc{i}#c2", f"doc{i}", f"doc{i}.pdf", "pdf", f"Unique body analysis {i} discussing separate topics.", word_count=35, chunk_index=2))

    indexer = VectorIndexer(model_name="all-MiniLM-L6-v2", device="cpu")
    embs = indexer.embed_texts([c.text for c in chunks])
    filtered_chunks = bp_filter.identify_and_filter(chunks, embs)

    # Assert 4 colluding students' body chunks (chunk_index == 2) are NOT excused as boilerplate
    for i in range(1, 5):
        body_chunk = next(c for c in filtered_chunks if c.chunk_id == f"doc{i}#c2")
        assert body_chunk.is_boilerplate is False, f"Collusive body chunk doc{i}#c2 was mistakenly excused as boilerplate!"

def test_boilerplate_excuses_prompt_at_chunk_index_1_after_title():
    # Test that opening template prompt occurring at chunk_index == 1 (after a title block)
    # across >= 3 docs IS correctly excused as institutional boilerplate.
    bp_filter = BoilerplateFilter(min_doc_frequency=3, similarity_threshold=0.88, short_chunk_word_limit=15)
    prompt_text = (
        "Case Study Challenge Brief 2026: Sustainable Urban Mobility Infrastructure. "
        "Teams are required to evaluate the capital deployment feasibility and regulatory constraints "
        "of transitioning municipal transit networks to zero-emission battery electric bus fleets."
    )

    chunks = []
    for i in range(1, 4):
        # chunk 0: distinct document title (>15 words)
        chunks.append(DocumentChunk(f"doc{i}#c0", f"doc{i}", f"doc{i}.pdf", "pdf", f"Strategic Electrification Master Plan Report Submission {i} for Municipal Transit.", word_count=16, chunk_index=0))
        # chunk 1: identical prompt header
        chunks.append(DocumentChunk(f"doc{i}#c1", f"doc{i}", f"doc{i}.pdf", "pdf", prompt_text, word_count=28, chunk_index=1))
        # chunk 2: original response
        chunks.append(DocumentChunk(f"doc{i}#c2", f"doc{i}", f"doc{i}.pdf", "pdf", f"Original unique response text for submission {i}.", word_count=25, chunk_index=2))

    indexer = VectorIndexer(model_name="all-MiniLM-L6-v2", device="cpu")
    embs = indexer.embed_texts([c.text for c in chunks])
    filtered_chunks = bp_filter.identify_and_filter(chunks, embs)

    # Assert prompt chunks at chunk_index == 1 ARE marked as boilerplate
    for i in range(1, 4):
        prompt_chunk = next(c for c in filtered_chunks if c.chunk_id == f"doc{i}#c1")
        assert prompt_chunk.is_boilerplate is True, f"Prompt chunk at index 1 doc{i}#c1 was not recognized as boilerplate!"
        ans_chunk = next(c for c in filtered_chunks if c.chunk_id == f"doc{i}#c2")
        assert ans_chunk.is_boilerplate is False, f"Original answer doc{i}#c2 was mistakenly marked as boilerplate!"

def test_boilerplate_excuses_opening_template_across_five_docs():
    # Hard Requirement 1(b): 5 documents sharing an identical opening competition prompt (chunk_index == 0)
    # ARE correctly excused as institutional boilerplate.
    bp_filter = BoilerplateFilter(min_doc_frequency=3, similarity_threshold=0.88, short_chunk_word_limit=15)
    prompt_text = (
        "Case Study Challenge Brief 2026: Sustainable Urban Mobility Infrastructure. "
        "Teams are required to evaluate the capital deployment feasibility and regulatory constraints "
        "of transitioning municipal transit networks to zero-emission battery electric bus fleets."
    )

    unique_responses = [
        "Deploying megawatt charging infrastructure at municipal bus depots requires dedicated high-voltage substation interconnects.",
        "Lithium iron phosphate battery cell degradation is primarily driven by high ambient operating temperatures and depth of discharge.",
        "Municipal green revenue bonds provide an optimal debt financing mechanism for fleet electrification capital expenditure.",
        "Empirical transit telemetry indicates regenerative braking recovers substantial kinetic energy along hilly municipal routes.",
        "Co-locating depot battery energy storage systems with solar photovoltaic arrays buffers peak electrical demand charges."
    ]

    chunks = []
    # 5 documents sharing identical opening prompt at chunk_index 0, with original answers at chunk_index 1
    for i in range(1, 6):
        chunks.append(DocumentChunk(f"sub{i}#c0", f"sub{i}", f"sub{i}.pdf", "pdf", prompt_text, word_count=28, chunk_index=0))
        chunks.append(DocumentChunk(f"sub{i}#c1", f"sub{i}", f"sub{i}.pdf", "pdf", unique_responses[i-1], word_count=20, chunk_index=1))

    indexer = VectorIndexer(model_name="all-MiniLM-L6-v2", device="cpu")
    embs = indexer.embed_texts([c.text for c in chunks])
    filtered_chunks = bp_filter.identify_and_filter(chunks, embs)

    # Assert all 5 opening prompt chunks ARE marked as boilerplate
    for i in range(1, 6):
        prompt_chunk = next(c for c in filtered_chunks if c.chunk_id == f"sub{i}#c0")
        assert prompt_chunk.is_boilerplate is True, f"Opening prompt sub{i}#c0 was not recognized as boilerplate!"
        ans_chunk = next(c for c in filtered_chunks if c.chunk_id == f"sub{i}#c1")
        assert ans_chunk.is_boilerplate is False, f"Original answer sub{i}#c1 was mistakenly marked as boilerplate!"

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

def test_tier2_paraphrase_escalates_to_medium():
    # Requirement: Tier 2 match (0.65 <= sim < 0.80) raises overall risk to at least MEDIUM
    config = {
        "risk_thresholds": {
            "high": {"peer_min": 50.0, "external_min": 40.0, "combined_peer_and_ai": {"peer_min": 30.0, "ai_min": 70.0}},
            "medium": {"peer_min": 20.0, "external_min": 20.0, "ai_min_with_peer": {"peer_min": 10.0, "ai_min": 70.0}, "ai_standalone_min": 85.0}
        }
    }
    rc = RiskCalculator(config)
    risk, explanation = rc.calculate_risk(peer_pct=0.0, external_pct=0.0, ai_prob=15.0, has_tier2=True, max_tier2_sim=0.68)
    assert risk == "MEDIUM", f"Expected MEDIUM for Tier 2 match, got {risk}"
    assert "Possible paraphrase" in explanation
    assert "0.68" in explanation

    # Check generated report for submission_19
    report_path = Path("./reports/submission_19_video_paraphrase_pitch.mp4.json")
    if report_path.exists():
        with open(report_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["total_integrity_risk"] == "MEDIUM"
        assert len(data["multimodal_matches"]) >= 1
        assert data["multimodal_matches"][0]["confidence_tier"] == "Possible paraphrase / review recommended (0.65-0.79)"

def test_case4_synthetic_cold_chain_leakage_diagnostics():
    """
    Reproduces and validates Failure Case 4 (Reference KB Domain Leakage).
    When scripts/generate_synthetic_dataset.py co-authored submission_03 and the original
    cold_chain_logistics.txt KB entry, it reused identical sentence structures and terminology.
    This test verifies that the resulting passage similarity (cosine ~0.876, Jaccard ~0.286)
    exceeds both the 0.80 cosine and 0.15 Jaccard thresholds, explaining exactly why submission_03
    registered an unintended 50% external match until the KB was decoupled with maritime text.
    """
    # Passage-level comparison (as extracted in case4_external_kb_leakage.txt)
    p1 = (
        "Establishing a resilient pharmaceutical cold chain requires continuous thermal monitoring "
        "between two and eight degrees Celsius across all intermediate warehouse hubs. Active refrigeration "
        "containers utilizing automated compressor cycles guarantee temperature stability during transcontinental flights, "
        "whereas passive thermal shippers rely on vacuum-insulated panels to protect vaccines during domestic road haulage."
    )
    p2 = (
        "Pharmaceutical cold chain logistics necessitate strict end-to-end temperature preservation "
        "ranging from ultra-cold cryopreservation between minus eighty degrees Celsius to standardized refrigerated "
        "storage between two and eight degrees Celsius. Active refrigeration containers utilizing automated compressor "
        "cycles offer reliable thermal control across transcontinental transit corridors, whereas passive thermal "
        "packaging systems rely upon vacuum-insulated panels and phase-change materials to mitigate ambient thermal "
        "excursions during multi-modal transshipment delays."
    )
    indexer = VectorIndexer(model_name="all-MiniLM-L6-v2", device="cpu")
    q_emb = indexer.embed_texts([p1])[0]
    r_emb = indexer.embed_texts([p2])[0]
    passage_cosine = float(np.dot(q_emb, r_emb))
    passage_jaccard = compute_jaccard_similarity(p1, p2)

    # Passage-level cosine is ~0.876 (reported as ~0.884 in case4)
    assert passage_cosine >= 0.85, f"Expected passage cosine >= 0.85, got {passage_cosine:.4f}"
    # Lexical overlap is 0.286 due to shared phrasing ("Active refrigeration containers utilizing...")
    assert passage_jaccard >= 0.20, f"Expected passage jaccard >= 0.20, got {passage_jaccard:.4f}"

    # Full chunk-level comparison (including DOCX title "Cold Chain Logistics and Temperature Assurance Strategy")
    chunk_text = "Cold Chain Logistics and Temperature Assurance Strategy. " + p1
    full_kb_text = p2 + " Real-time Internet of Things sensor telemetry enables immediate intervention."
    chunk_cosine = float(np.dot(indexer.embed_texts([chunk_text])[0], indexer.embed_texts([full_kb_text])[0]))
    
    # Chunk-level cosine settles at ~0.811
    assert 0.80 <= chunk_cosine <= 0.85, f"Expected chunk cosine in [0.80, 0.85], got {chunk_cosine:.4f}"

    # Confirm that under the external detection rule (cosine >= 0.80 and (cosine >= 0.90 or jaccard >= 0.15)),
    # this pair WOULD trigger an external match because jaccard (0.286) >= 0.15.
    would_be_flagged = (passage_cosine >= 0.80) and (passage_cosine >= 0.90 or passage_jaccard >= 0.15)
    assert would_be_flagged is True, "Expected this synthetic leakage pair to be flagged under external rule"

def test_external_detector_rejects_unrelated_domain_text():
    """
    Validates that ExternalDetector correctly rejects independent documents with non-overlapping wording,
    ensuring zero false positives on genuine submissions against the active knowledge base.
    """
    from src.detectors.external_detector import ExternalDetector
    from src.normalizer.chunker import DocumentChunk
    indexer = VectorIndexer(model_name="all-MiniLM-L6-v2", device="cpu")
    ext_detector = ExternalDetector(vector_indexer=indexer, kb_dir="./external_kb", chunk_threshold=0.80)
    chunker = DocumentChunker(250, 50, 15)
    ext_detector.load_and_index_kb(chunker)

    # Test an original clean submission chunk (EV bus depot charging)
    clean_chunk = DocumentChunk(
        chunk_id="test_clean#c0",
        doc_id="test_clean",
        file_name="test_clean.pdf",
        modality="pdf",
        text="Deploying megawatt charging infrastructure at municipal bus depots requires dedicated high-voltage substation interconnects."
    )
    clean_emb = indexer.embed_texts([clean_chunk.text])
    results = ext_detector.analyze_document_external_matches("test_clean", [clean_chunk], clean_emb)
    assert results["external_similarity_percentage"] == 0.0
    assert len(results["external_matches"]) == 0

