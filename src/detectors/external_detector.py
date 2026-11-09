"""
External Plagiarism Detector against a local Reference Knowledge Base.
Indexes public-domain / Wikipedia reference texts with source URLs
and computes external match coverage percentages with source citations.
"""

from typing import List, Dict, Any, Optional
import os
import json
import logging
from pathlib import Path

from src.normalizer.chunker import DocumentChunk, DocumentChunker
from src.indexer.vector_indexer import VectorIndexer, MatchResult
from src.extractors.base_extractor import ExtractedDocument
from src.normalizer.normalizer import clean_text

logger = logging.getLogger("external_detector")

class ExternalDetector:
    def __init__(
        self,
        vector_indexer: VectorIndexer,
        kb_dir: str = "./external_kb",
        chunk_threshold: float = 0.80
    ):
        self.indexer = vector_indexer
        self.kb_dir = Path(kb_dir)
        self.chunk_threshold = chunk_threshold
        self.kb_chunks: List[DocumentChunk] = []
        self.source_metadata: Dict[str, Dict[str, str]] = {}

    def load_and_index_kb(self, chunker: DocumentChunker):
        """Loads and chunks reference texts from external_kb directory."""
        if not self.kb_dir.exists():
            logger.warning(f"External KB directory does not exist: {self.kb_dir}")
            return

        meta_file = self.kb_dir / "sources_manifest.json"
        if meta_file.exists():
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    self.source_metadata = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load sources_manifest.json: {e}")

        kb_chunks: List[DocumentChunk] = []
        for file_path in self.kb_dir.glob("*.txt"):
            if file_path.name == "sources_manifest.json":
                continue
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                
                doc_id = f"kb_{file_path.stem}"
                chunks = chunker._chunk_generic_text(
                    doc_id=doc_id,
                    file_name=file_path.name,
                    modality="kb",
                    raw_text=content
                )
                kb_chunks.extend(chunks)
            except Exception as e:
                logger.warning(f"Error loading KB file {file_path}: {e}")

        self.kb_chunks = kb_chunks
        logger.info(f"Loaded {len(kb_chunks)} external reference chunks from {self.kb_dir}.")

    def analyze_document_external_matches(
        self,
        doc_id: str,
        query_chunks: List[DocumentChunk],
        query_embeddings: Any
    ) -> Dict[str, Any]:
        """Calculates external reference similarity coverage and citations."""
        active_chunks = [c for c in query_chunks if not c.is_boilerplate]
        if not active_chunks:
            return {
                "external_similarity_percentage": 0.0,
                "external_matches": []
            }

        matched_chunk_ids = set()
        external_matches: List[Dict[str, Any]] = []

        for i, q_chunk in enumerate(query_chunks):
            if q_chunk.is_boilerplate:
                continue

            q_vec = query_embeddings[i]
            results = self.indexer.search_matches_for_chunk(
                query_chunk=q_chunk,
                query_embedding=q_vec,
                top_k=3,
                min_similarity=self.chunk_threshold,
                exclude_boilerplate=False
            )

            kb_results = [r for r in results if r.is_external]
            if kb_results:
                matched_chunk_ids.add(q_chunk.chunk_id)
                top_match = kb_results[0]
                t_chunk = top_match.matched_chunk
                
                meta = self.source_metadata.get(t_chunk.doc_id, {})
                source_url = meta.get("url", f"https://en.wikipedia.org/wiki/{t_chunk.file_name.replace('.txt', '')}")
                source_title = meta.get("title", t_chunk.file_name)

                # Sentence alignment
                q_sent = q_chunk.sentences[0] if q_chunk.sentences else q_chunk.text
                t_sent = t_chunk.sentences[0] if t_chunk.sentences else t_chunk.text

                external_matches.append({
                    "source_title": source_title,
                    "source_url": source_url,
                    "matched_file": t_chunk.file_name,
                    "similarity_score": round(top_match.cosine_similarity, 2),
                    "query_passage": q_sent,
                    "matched_passage": t_sent
                })

        coverage_pct = round((len(matched_chunk_ids) / len(active_chunks)) * 100.0, 1)

        return {
            "external_similarity_percentage": coverage_pct,
            "external_matches": external_matches
        }
