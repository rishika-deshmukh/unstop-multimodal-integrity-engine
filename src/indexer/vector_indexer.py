"""
Dense vector indexing and retrieval engine using Sentence-Transformers and FAISS.
Enforces strict doc_id self-match exclusion, cosine similarity normalization,
and seamless multi-modal cross-referencing.
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
import logging
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
import faiss

from src.normalizer.chunker import DocumentChunk

logger = logging.getLogger("vector_indexer")

@dataclass
class MatchResult:
    query_chunk: DocumentChunk
    matched_chunk: DocumentChunk
    cosine_similarity: float
    is_multimodal: bool
    is_external: bool

class VectorIndexer:
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        device: str = "cpu"
    ):
        self.model_name = model_name
        self.device = device
        self._embedder = None
        self.chunks: List[DocumentChunk] = []
        self.embeddings: Optional[np.ndarray] = None
        self.faiss_index: Optional[faiss.IndexFlatIP] = None
        self.dimension: int = 384

    @property
    def embedder(self) -> SentenceTransformer:
        if self._embedder is None:
            logger.info(f"Loading embedding model '{self.model_name}' on {self.device}...")
            self._embedder = SentenceTransformer(self.model_name, device=self.device)
            if hasattr(self._embedder, "get_embedding_dimension"):
                self.dimension = self._embedder.get_embedding_dimension()
            else:
                self.dimension = self._embedder.get_sentence_embedding_dimension()
        return self._embedder

    def embed_texts(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Generates L2-normalized embeddings for a list of text strings."""
        if not texts:
            return np.empty((0, self.dimension), dtype=np.float32)
        embs = self.embedder.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        return embs.astype(np.float32)

    def index_chunks(self, chunks: List[DocumentChunk], precomputed_embeddings: Optional[np.ndarray] = None):
        """Indexes all document chunks into FAISS."""
        self.chunks = chunks
        if not chunks:
            self.embeddings = np.empty((0, self.dimension), dtype=np.float32)
            self.faiss_index = faiss.IndexFlatIP(self.dimension)
            return

        if precomputed_embeddings is not None and len(precomputed_embeddings) == len(chunks):
            self.embeddings = precomputed_embeddings.astype(np.float32)
        else:
            texts = [c.text for c in chunks]
            self.embeddings = self.embed_texts(texts)

        # Build FAISS IndexFlatIP (Inner Product on L2-normalized vectors == Cosine Similarity)
        self.dimension = self.embeddings.shape[1]
        self.faiss_index = faiss.IndexFlatIP(self.dimension)
        self.faiss_index.add(self.embeddings)
        logger.info(f"Indexed {len(chunks)} chunks into FAISS vector space (dim={self.dimension}).")

    def search_matches_for_chunk(
        self,
        query_chunk: DocumentChunk,
        query_embedding: np.ndarray,
        top_k: int = 10,
        min_similarity: float = 0.80,
        exclude_boilerplate: bool = True
    ) -> List[MatchResult]:
        """
        Searches index for matching chunks with strict self-doc_id exclusion.
        Returns matches above min_similarity threshold.
        """
        if self.faiss_index is None or len(self.chunks) == 0:
            return []

        # Ensure query_embedding is 2D and float32
        q_vec = query_embedding.reshape(1, -1).astype(np.float32)
        # Fetch extra candidates to account for self-matches or boilerplate exclusion
        k_fetch = min(len(self.chunks), max(top_k * 3, 20))
        scores, indices = self.faiss_index.search(q_vec, k_fetch)

        matches: List[MatchResult] = []
        for sim, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.chunks):
                continue

            target_chunk = self.chunks[idx]

            # Strict self-match exclusion: query doc cannot match itself
            if target_chunk.doc_id == query_chunk.doc_id:
                continue

            # Exclude boilerplate template matches
            if exclude_boilerplate and target_chunk.is_boilerplate:
                continue

            sim_val = round(float(sim), 4)
            if sim_val < min_similarity:
                continue

            is_external = (target_chunk.modality == "kb")
            is_multimodal = (
                (query_chunk.modality == "mp4" and target_chunk.modality in ("pdf", "docx")) or
                (query_chunk.modality in ("pdf", "docx") and target_chunk.modality == "mp4")
            )

            matches.append(
                MatchResult(
                    query_chunk=query_chunk,
                    matched_chunk=target_chunk,
                    cosine_similarity=sim_val,
                    is_multimodal=is_multimodal,
                    is_external=is_external
                )
            )

            if len(matches) >= top_k:
                break

        return matches
