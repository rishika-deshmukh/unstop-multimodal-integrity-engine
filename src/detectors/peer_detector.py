"""
Internal Peer-to-Peer & Cross-Modal Similarity Detector.
Computes coverage-based peer similarity percentages, separates unimodal and multimodal matches,
and performs fine-grained sentence-level re-matching for concise, 30-second human verification.
"""

from typing import List, Dict, Any, Tuple
import numpy as np
import logging

from src.normalizer.chunker import DocumentChunk
from src.indexer.vector_indexer import VectorIndexer, MatchResult
from src.utils.text_metrics import (
    compute_jaccard_similarity,
    compute_normalized_levenshtein_similarity
)

logger = logging.getLogger("peer_detector")

class PeerDetector:
    def __init__(
        self,
        vector_indexer: VectorIndexer,
        chunk_threshold: float = 0.80,
        sentence_threshold: float = 0.75,
        lexical_jaccard_low_threshold: float = 0.35
    ):
        self.indexer = vector_indexer
        self.chunk_threshold = chunk_threshold
        self.sentence_threshold = sentence_threshold
        self.lexical_jaccard_low_threshold = lexical_jaccard_low_threshold

    def align_best_sentences(
        self,
        query_chunk: DocumentChunk,
        target_chunk: DocumentChunk
    ) -> Tuple[str, str, float]:
        """
        Extracts the most salient matching sentence pair from query and target chunks.
        Avoids dumping giant 300-token blocks, ensuring fast human review (<30s).
        """
        q_sents = query_chunk.sentences if query_chunk.sentences else [query_chunk.text]
        t_sents = target_chunk.sentences if target_chunk.sentences else [target_chunk.text]

        if len(q_sents) == 1 and len(t_sents) == 1:
            return q_sents[0], t_sents[0], 1.0

        # Embed sentences
        q_embs = self.indexer.embed_texts(q_sents)
        t_embs = self.indexer.embed_texts(t_sents)

        sim_matrix = np.dot(q_embs, t_embs.T)
        best_idx = np.unravel_index(np.argmax(sim_matrix), sim_matrix.shape)
        best_sim = float(sim_matrix[best_idx])
        best_q_sent = q_sents[best_idx[0]]
        best_t_sent = t_sents[best_idx[1]]

        return best_q_sent, best_t_sent, round(best_sim, 4)

    def analyze_document_peer_matches(
        self,
        doc_id: str,
        query_chunks: List[DocumentChunk],
        query_embeddings: np.ndarray
    ) -> Dict[str, Any]:
        """
        Evaluates peer similarity for all chunks of a document against internal corpus.
        Returns coverage percentage and structured lists of peer and multimodal matches.
        """
        active_chunks = [c for c in query_chunks if not c.is_boilerplate]
        if not active_chunks:
            return {
                "peer_similarity_percentage": 0.0,
                "peer_matches": [],
                "multimodal_matches": []
            }

        matched_chunk_ids = set()
        peer_matches: List[Dict[str, Any]] = []
        multimodal_matches: List[Dict[str, Any]] = []

        for i, q_chunk in enumerate(query_chunks):
            if q_chunk.is_boilerplate:
                continue

            q_vec = query_embeddings[i]
            # Search matches in index
            results = self.indexer.search_matches_for_chunk(
                query_chunk=q_chunk,
                query_embedding=q_vec,
                top_k=5,
                min_similarity=self.chunk_threshold,
                exclude_boilerplate=True
            )

            # Filter only internal peer matches (not external kb)
            internal_results = [r for r in results if not r.is_external]
            if internal_results:
                matched_chunk_ids.add(q_chunk.chunk_id)

                # Take top match for detailed explanation
                top_match = internal_results[0]
                t_chunk = top_match.matched_chunk
                
                # Align exact offending sentences
                q_sent, t_sent, sent_sim = self.align_best_sentences(q_chunk, t_chunk)
                
                # Compute lexical metrics for contrast (Scenario 2)
                jaccard = compute_jaccard_similarity(q_sent, t_sent)
                lev_sim = compute_normalized_levenshtein_similarity(q_sent, t_sent)

                # Build location metadata dict conforming to schema
                location: Dict[str, Any] = {}
                if q_chunk.page_number is not None:
                    location["query_page"] = q_chunk.page_number
                if q_chunk.timestamp_str is not None:
                    location["query_timestamp"] = q_chunk.timestamp_str

                if t_chunk.page_number is not None:
                    location["matched_page"] = t_chunk.page_number
                if t_chunk.timestamp_str is not None:
                    location["matched_timestamp"] = t_chunk.timestamp_str

                match_record = {
                    "matched_file": t_chunk.file_name,
                    "similarity_score": round(top_match.cosine_similarity, 2),
                    "lexical_jaccard": jaccard,
                    "lexical_levenshtein": lev_sim,
                    "is_paraphrase": bool(top_match.cosine_similarity >= self.chunk_threshold and jaccard < self.lexical_jaccard_low_threshold),
                    "query_passage": q_sent,
                    "matched_passage": t_sent,
                    "location": location
                }

                if top_match.is_multimodal:
                    multimodal_matches.append(match_record)
                else:
                    peer_matches.append(match_record)

        # Coverage-based peer similarity percentage
        coverage_pct = round((len(matched_chunk_ids) / len(active_chunks)) * 100.0, 1)

        return {
            "peer_similarity_percentage": coverage_pct,
            "peer_matches": peer_matches,
            "multimodal_matches": multimodal_matches
        }
