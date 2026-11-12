"""
Multimodal Submission Integrity & Plagiarism Detection Engine.
Main CLI entrypoint. Evaluates PDF, DOCX, and MP4 submissions for:
1. Internal peer-to-peer similarity (unimodal and cross-modal).
2. External reference plagiarism against a knowledge base.
3. Supervised and statistical AI-generation likelihood.
4. Institutional template / prompt header discounting.
5. Explainable, human-verifiable citations with page numbers and video timestamps.
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
import torch

from src.utils.config_loader import load_config
from src.utils.ffmpeg_setup import ensure_ffmpeg_available
from src.extractors.dispatcher import DocumentParser
from src.extractors.base_extractor import ExtractedDocument
from src.normalizer.chunker import DocumentChunker, DocumentChunk
from src.filters.boilerplate_filter import BoilerplateFilter
from src.indexer.vector_indexer import VectorIndexer
from src.detectors.peer_detector import PeerDetector
from src.detectors.external_detector import ExternalDetector
from src.detectors.ai_detector import AIDetector
from src.detectors.risk_calculator import RiskCalculator
from src.reporter.json_reporter import format_json_report, write_json_report
from src.reporter.markdown_reporter import generate_markdown_report, write_markdown_report
from src.reporter.batch_summary import generate_summary_matrix

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("integrity_engine")

def set_deterministic_seed(seed: int = 42):
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def run_pipeline(input_dir: str, output_dir: str, config_path: str = "config.yaml"):
    set_deterministic_seed(42)
    config = load_config(config_path)
    ensure_ffmpeg_available()

    in_path = Path(input_dir)
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    if not in_path.exists():
        logger.error(f"Input directory not found: {in_path}")
        sys.exit(1)

    # 1. Discover files
    valid_exts = {".pdf", ".docx", ".doc", ".mp4", ".mkv", ".mov", ".avi"}
    candidate_files = sorted([f for f in in_path.iterdir() if f.suffix.lower() in valid_exts and f.is_file()])
    logger.info(f"Discovered {len(candidate_files)} submission files in '{input_dir}'.")

    if not candidate_files:
        logger.warning("No supported submission files found.")
        return

    # 2. Initialize Components
    models_cfg = config.get("models", {})
    chunk_cfg = config.get("chunking", {})
    sim_cfg = config.get("similarity", {})
    bp_cfg = config.get("boilerplate_filter", {})
    paths_cfg = config.get("paths", {})

    device = models_cfg.get("device", "cpu")
    doc_parser = DocumentParser(whisper_model=models_cfg.get("whisper_model", "base"), device=device)
    chunker = DocumentChunker(
        chunk_size_tokens=chunk_cfg.get("chunk_size_tokens", 250),
        chunk_overlap_tokens=chunk_cfg.get("chunk_overlap_tokens", 50),
        min_chunk_words=chunk_cfg.get("min_chunk_words", 15)
    )
    vector_indexer = VectorIndexer(model_name=models_cfg.get("embedding_model", "all-MiniLM-L6-v2"), device=device)
    boilerplate_filter = BoilerplateFilter(
        min_doc_frequency=bp_cfg.get("min_doc_frequency", 3),
        similarity_threshold=bp_cfg.get("similarity_threshold", 0.88),
        short_chunk_word_limit=bp_cfg.get("short_chunk_word_limit", 15)
    )
    external_detector = ExternalDetector(
        vector_indexer=vector_indexer,
        kb_dir=paths_cfg.get("external_kb_dir", "./external_kb"),
        chunk_threshold=sim_cfg.get("chunk_match_threshold", 0.80)
    )
    peer_detector = PeerDetector(
        vector_indexer=vector_indexer,
        chunk_threshold=sim_cfg.get("chunk_match_threshold", 0.80),
        sentence_threshold=sim_cfg.get("sentence_alignment_threshold", 0.75),
        lexical_jaccard_low_threshold=sim_cfg.get("lexical_jaccard_low_threshold", 0.35),
        review_threshold=sim_cfg.get("review_recommended_threshold", 0.65)
    )
    ai_detector = AIDetector(
        classifier_model=models_cfg.get("ai_detector_model", "roberta-base-openai-detector"),
        gpt2_model=models_cfg.get("gpt2_model", "gpt2"),
        device=device
    )
    risk_calculator = RiskCalculator(config)

    # 3. Load & Index External Knowledge Base
    external_detector.load_and_index_kb(chunker)
    all_chunks: List[DocumentChunk] = list(external_detector.kb_chunks)

    # 4. Ingest Submissions
    logger.info("Extracting text and chunking submissions...")
    extracted_docs: Dict[str, ExtractedDocument] = {}
    doc_chunks_map: Dict[str, List[DocumentChunk]] = {}

    for fpath in candidate_files:
        logger.info(f"Parsing: {fpath.name}")
        doc = doc_parser.parse(fpath)
        extracted_docs[doc.doc_id] = doc

        if doc.is_usable:
            chunks = chunker.chunk_document(doc)
            doc_chunks_map[doc.doc_id] = chunks
            all_chunks.extend(chunks)
        else:
            logger.warning(f"File marked unusable: {doc.doc_id} -> {doc.status} ({doc.warning_message})")
            doc_chunks_map[doc.doc_id] = []

    # 5. Embed All Chunks & Filter Boilerplate
    logger.info(f"Computing embeddings for {len(all_chunks)} total chunks (Corpus + External KB)...")
    if all_chunks:
        corpus_texts = [c.text for c in all_chunks]
        all_embeddings = vector_indexer.embed_texts(corpus_texts)
        
        # Apply boilerplate template filter (Scenario 4) on corpus chunks
        if bp_cfg.get("enabled", True):
            boilerplate_filter.identify_and_filter(all_chunks, all_embeddings)

        # Index in FAISS
        vector_indexer.index_chunks(all_chunks, precomputed_embeddings=all_embeddings)

    # 6. Evaluate Each Submission Document
    reports_map: Dict[str, Dict[str, Any]] = {}
    doc_ids = [f.name for f in candidate_files]

    # Precompute AI detection scores strictly using detector models (no filename heuristics)
    ai_threshold = config.get("risk_thresholds", {}).get("medium", {}).get("ai_min_with_peer", {}).get("ai_min", 50.0)
    doc_ai_results_map: Dict[str, Dict[str, Any]] = {}
    for d_id, doc_obj in extracted_docs.items():
        if doc_obj and doc_obj.is_usable and doc_obj.raw_text:
            doc_ai_results_map[d_id] = ai_detector.analyze(doc_obj.raw_text)
        else:
            doc_ai_results_map[d_id] = {"ai_generated_probability": 0.0}

    for doc_id in doc_ids:
        doc = extracted_docs.get(doc_id)
        chunks = doc_chunks_map.get(doc_id, [])

        # Handle corrupt, empty, or silent files (Scenario 3)
        if not doc or not doc.is_usable:
            status = doc.status if doc else "SKIPPED_CORRUPT"
            warn_msg = doc.warning_message if doc else "Unknown parsing error."
            json_rep = format_json_report(
                doc_id=doc_id,
                total_integrity_risk="FLAGGED",
                peer_sim_pct=0.0,
                ext_sim_pct=0.0,
                ai_prob=0.0,
                peer_matches=[],
                multimodal_matches=[],
                external_matches=[],
                explanations=f"Submission flagged or skipped: {warn_msg}",
                status=status,
                warning_message=warn_msg
            )
            md_rep = generate_markdown_report(
                doc_id=doc_id,
                total_integrity_risk="FLAGGED",
                peer_sim_pct=0.0,
                ext_sim_pct=0.0,
                ai_prob=0.0,
                peer_matches=[],
                multimodal_matches=[],
                external_matches=[],
                discounted_boilerplate=[],
                ai_signals={},
                explanations=f"Submission flagged or skipped: {warn_msg}",
                status=status,
                warning_message=warn_msg
            )
            reports_map[doc_id] = json_rep
            write_json_report(json_rep, out_path / f"{doc_id}.json")
            write_markdown_report(md_rep, out_path / f"{doc_id}.md")
            continue

        # Valid document processing
        # Embed query chunks
        q_texts = [c.text for c in chunks]
        q_embs = vector_indexer.embed_texts(q_texts)

        # Signal 1: Peer-to-Peer & Multimodal
        peer_results = peer_detector.analyze_document_peer_matches(doc_id, chunks, q_embs)
        peer_pct = peer_results["peer_similarity_percentage"]
        peer_matches = peer_results["peer_matches"]
        mm_matches = peer_results["multimodal_matches"]

        # Signal 2: External Knowledge Base Matches
        ext_results = external_detector.analyze_document_external_matches(doc_id, chunks, q_embs)
        ext_pct = ext_results["external_similarity_percentage"]
        ext_matches = ext_results["external_matches"]

        # Signal 3: AI-Generation Estimation (using precomputed detector score)
        ai_results = doc_ai_results_map.get(doc_id, {"ai_generated_probability": 0.0})
        ai_prob = ai_results["ai_generated_probability"]

        # Multi-Signal Risk Classification (Tier 2 matches in 0.65-0.80 range elevate risk to MEDIUM)
        has_tier2 = peer_results.get("has_tier2_matches", False)
        max_tier2_sim = peer_results.get("max_tier2_sim", 0.0)
        risk_level, explanation_str = risk_calculator.calculate_risk(
            peer_pct=peer_pct,
            external_pct=ext_pct,
            ai_prob=ai_prob,
            has_tier2=has_tier2,
            max_tier2_sim=max_tier2_sim
        )

        # Check for dual-AI prompt convergence on peer matches strictly by detector score (no filename heuristics)
        is_current_ai = (ai_prob >= ai_threshold)
        for m in peer_matches + mm_matches:
            target_name = m.get("matched_file", "")
            target_ai_prob = doc_ai_results_map.get(target_name, {}).get("ai_generated_probability", 0.0)
            is_target_ai = (target_ai_prob >= ai_threshold)
            if is_current_ai and is_target_ai:
                dual_ai_note = "Reviewer note: High semantic similarity between AI-generated submissions may stem from independent generation using an identical assignment prompt rather than direct student-to-student copying."
                m["attribution_note"] = f"{m.get('attribution_note', '')} {dual_ai_note}".strip()
                if "independent generation" not in explanation_str:
                    explanation_str += f" | {dual_ai_note}"

        # Boilerplate records discounted for this document
        discounted_bp = boilerplate_filter.get_discounted_for_doc(doc_id)

        # Generate Reports
        json_rep = format_json_report(
            doc_id=doc_id,
            total_integrity_risk=risk_level,
            peer_sim_pct=peer_pct,
            ext_sim_pct=ext_pct,
            ai_prob=ai_prob,
            peer_matches=peer_matches,
            multimodal_matches=mm_matches,
            external_matches=ext_matches,
            explanations=explanation_str,
            status="SUCCESS"
        )
        md_rep = generate_markdown_report(
            doc_id=doc_id,
            total_integrity_risk=risk_level,
            peer_sim_pct=peer_pct,
            ext_sim_pct=ext_pct,
            ai_prob=ai_prob,
            peer_matches=peer_matches,
            multimodal_matches=mm_matches,
            external_matches=ext_matches,
            discounted_boilerplate=discounted_bp,
            ai_signals=ai_results,
            explanations=explanation_str,
            status="SUCCESS"
        )

        reports_map[doc_id] = json_rep
        write_json_report(json_rep, out_path / f"{doc_id}.json")
        write_markdown_report(md_rep, out_path / f"{doc_id}.md")

    # 7. Compute Pairwise Similarity Matrix
    n_docs = len(doc_ids)
    pairwise_matrix = np.zeros((n_docs, n_docs), dtype=float)

    for i in range(n_docs):
        for j in range(n_docs):
            if i == j:
                pairwise_matrix[i, j] = 1.0
            else:
                chunks_a = [c for c in doc_chunks_map.get(doc_ids[i], []) if not c.is_boilerplate]
                chunks_b = [c for c in doc_chunks_map.get(doc_ids[j], []) if not c.is_boilerplate]
                if chunks_a and chunks_b:
                    embs_a = vector_indexer.embed_texts([c.text for c in chunks_a])
                    embs_b = vector_indexer.embed_texts([c.text for c in chunks_b])
                    sims = np.dot(embs_a, embs_b.T)
                    pairwise_matrix[i, j] = round(float(np.max(sims)), 2)

    # 8. Export Batch Summary Matrix
    generate_summary_matrix(doc_ids, pairwise_matrix, reports_map, out_path)
    logger.info(f"Verification complete! Reports generated in '{output_dir}'.")

def main():
    parser = argparse.ArgumentParser(
        description="Multimodal Submission Integrity & Plagiarism Detection Engine"
    )
    parser.add_argument(
        "--input_dir",
        type=str,
        default="./sample_submissions",
        help="Path to folder containing candidate submissions (.pdf, .docx, .mp4)"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./reports",
        help="Path to destination directory for generated verification reports"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to configuration YAML file"
    )

    args = parser.parse_args()
    run_pipeline(input_dir=args.input_dir, output_dir=args.output_dir, config_path=args.config)

if __name__ == "__main__":
    main()
