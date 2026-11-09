"""
Corpus-wide boilerplate and institutional template filtering module.
Detects repeated prompt headers across >= 3 documents and discounts short boilerplate fragments
to prevent false-positive plagiarism flags on benign shared competition instructions (Scenario 4).
"""

from typing import List, Dict, Set, Tuple
import numpy as np
import logging

from src.normalizer.chunker import DocumentChunk
from src.utils.text_metrics import compute_jaccard_similarity

logger = logging.getLogger("boilerplate_filter")

class BoilerplateFilter:
    def __init__(
        self,
        min_doc_frequency: int = 3,
        similarity_threshold: float = 0.88,
        short_chunk_word_limit: int = 15
    ):
        self.min_doc_frequency = min_doc_frequency
        self.similarity_threshold = similarity_threshold
        self.short_chunk_word_limit = short_chunk_word_limit
        self.discounted_records: List[Dict[str, any]] = []

    def identify_and_filter(
        self,
        chunks: List[DocumentChunk],
        embeddings: np.ndarray = None
    ) -> List[DocumentChunk]:
        """
        Analyzes corpus chunks, identifies boilerplate/template text occurring across
        >= min_doc_frequency documents or under word limit, and tags chunks accordingly.
        """
        self.discounted_records.clear()
        doc_ids = set(c.doc_id for c in chunks)
        
        # 1. First pass: Filter short fragments
        for c in chunks:
            if c.word_count < self.short_chunk_word_limit:
                c.is_boilerplate = True
                c.discount_reason = f"Short fragment ({c.word_count} words < {self.short_chunk_word_limit})"
                self.discounted_records.append({
                    "chunk_id": c.chunk_id,
                    "doc_id": c.doc_id,
                    "reason": c.discount_reason,
                    "text_snippet": c.text[:120] + "..." if len(c.text) > 120 else c.text,
                    "doc_count": 1
                })

        # 2. Second pass: Document frequency clustering using embeddings or fast Jaccard
        if len(doc_ids) >= self.min_doc_frequency:
            n = len(chunks)
            if embeddings is not None and len(embeddings) == n:
                # Fast cosine matrix: embeddings are assumed normalized
                sim_matrix = np.dot(embeddings, embeddings.T)
                for i in range(n):
                    if chunks[i].is_boilerplate:
                        continue
                    # Find matching documents
                    matching_docs: Set[str] = {chunks[i].doc_id}
                    matching_indices = []
                    for j in range(n):
                        if i != j and sim_matrix[i, j] >= self.similarity_threshold:
                            matching_docs.add(chunks[j].doc_id)
                            matching_indices.append(j)

                    if len(matching_docs) >= self.min_doc_frequency:
                        # Mark chunk i and all its matching counterparts as boilerplate
                        chunks[i].is_boilerplate = True
                        chunks[i].discount_reason = (
                            f"Common case template / problem prompt shared across {len(matching_docs)} documents"
                        )
                        self.discounted_records.append({
                            "chunk_id": chunks[i].chunk_id,
                            "doc_id": chunks[i].doc_id,
                            "reason": chunks[i].discount_reason,
                            "text_snippet": chunks[i].text[:120] + "..." if len(chunks[i].text) > 120 else chunks[i].text,
                            "doc_count": len(matching_docs)
                        })
                        for idx in matching_indices:
                            chunks[idx].is_boilerplate = True
                            chunks[idx].discount_reason = (
                                f"Common case template / problem prompt shared across {len(matching_docs)} documents"
                            )
            else:
                # Fallback to lexical Jaccard clustering
                for i in range(n):
                    if chunks[i].is_boilerplate:
                        continue
                    matching_docs = {chunks[i].doc_id}
                    for j in range(i + 1, n):
                        if chunks[i].doc_id != chunks[j].doc_id:
                            if compute_jaccard_similarity(chunks[i].text, chunks[j].text) >= 0.70:
                                matching_docs.add(chunks[j].doc_id)

                    if len(matching_docs) >= self.min_doc_frequency:
                        chunks[i].is_boilerplate = True
                        chunks[i].discount_reason = (
                            f"Common case template / problem prompt shared across {len(matching_docs)} documents"
                        )
                        self.discounted_records.append({
                            "chunk_id": chunks[i].chunk_id,
                            "doc_id": chunks[i].doc_id,
                            "reason": chunks[i].discount_reason,
                            "text_snippet": chunks[i].text[:120] + "..." if len(chunks[i].text) > 120 else chunks[i].text,
                            "doc_count": len(matching_docs)
                        })

        logger.info(f"Boilerplate filtering complete: tagged {len(self.discounted_records)} chunk occurrences.")
        return chunks

    def get_discounted_for_doc(self, doc_id: str) -> List[Dict[str, any]]:
        """Returns list of discounted boilerplate chunks for a specific document."""
        return [r for r in self.discounted_records if r["doc_id"] == doc_id]
