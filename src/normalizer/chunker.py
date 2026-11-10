"""
Metadata-preserving sliding window chunker.
Segments documents into 200-400 token windows with overlap while maintaining
exact page numbers for PDFs and timestamp ranges for MP4 videos.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path

from src.extractors.base_extractor import ExtractedDocument, PageContent, AudioSegment
from src.normalizer.normalizer import clean_text, split_into_sentences
from src.utils.text_metrics import format_timestamp

@dataclass
class DocumentChunk:
    chunk_id: str
    doc_id: str
    file_name: str
    modality: str  # 'pdf', 'docx', 'mp4', 'kb'
    text: str
    sentences: List[str] = field(default_factory=list)
    page_number: Optional[int] = None
    timestamp_str: Optional[str] = None
    start_seconds: Optional[float] = None
    end_seconds: Optional[float] = None
    word_count: int = 0
    chunk_index: int = 0
    is_boilerplate: bool = False
    discount_reason: Optional[str] = None

class DocumentChunker:
    def __init__(
        self,
        chunk_size_tokens: int = 250,
        chunk_overlap_tokens: int = 50,
        min_chunk_words: int = 15
    ):
        self.chunk_size_tokens = chunk_size_tokens
        self.chunk_overlap_tokens = chunk_overlap_tokens
        self.min_chunk_words = min_chunk_words

    def chunk_document(self, doc: ExtractedDocument) -> List[DocumentChunk]:
        """Dispatches document to modality-specific chunking strategy."""
        if not doc.is_usable:
            return []

        if doc.modality == "pdf" and doc.pages:
            return self._chunk_pdf(doc)
        elif doc.modality == "mp4" and doc.audio_segments:
            return self._chunk_video(doc)
        elif doc.modality == "docx":
            return self._chunk_docx(doc)
        else:
            return self._chunk_generic_text(doc.doc_id, doc.file_name, doc.modality, doc.raw_text)

    def _chunk_pdf(self, doc: ExtractedDocument) -> List[DocumentChunk]:
        """Chunks PDF document preserving exact page-level citations and paragraph boundaries."""
        chunks: List[DocumentChunk] = []
        chunk_idx = 0

        for page in doc.pages:
            page_text = clean_text(page.text)
            if not page_text:
                continue

            # Split by double newline to respect paragraphs
            paragraphs = [p.strip() for p in page_text.split("\n\n") if p.strip()]
            for p in paragraphs:
                p_sents = split_into_sentences(p)
                if not p_sents:
                    continue
                p_chunks = self._slide_sentences(
                    sentences=p_sents,
                    doc_id=doc.doc_id,
                    file_name=doc.file_name,
                    modality="pdf",
                    page_number=page.page_number,
                    start_idx=chunk_idx
                )
                chunks.extend(p_chunks)
                chunk_idx += len(p_chunks)

        return chunks

    def _chunk_docx(self, doc: ExtractedDocument) -> List[DocumentChunk]:
        """Chunks DOCX document preserving paragraph structures."""
        chunks: List[DocumentChunk] = []
        chunk_idx = 0
        paragraphs = doc.paragraphs if doc.paragraphs else [p.strip() for p in doc.raw_text.split("\n\n") if p.strip()]

        for p in paragraphs:
            cleaned_p = clean_text(p)
            p_sents = split_into_sentences(cleaned_p)
            if not p_sents:
                continue
            p_chunks = self._slide_sentences(
                sentences=p_sents,
                doc_id=doc.doc_id,
                file_name=doc.file_name,
                modality="docx",
                page_number=1,
                start_idx=chunk_idx
            )
            chunks.extend(p_chunks)
            chunk_idx += len(p_chunks)

        return chunks

    def _chunk_video(self, doc: ExtractedDocument) -> List[DocumentChunk]:
        """
        Chunks MP4 video aligning directly with Whisper segment timestamps.
        Groups adjacent short segments to form meaningful topical windows.
        """
        chunks: List[DocumentChunk] = []
        segments = doc.audio_segments
        if not segments:
            return []

        curr_texts: List[str] = []
        curr_sents: List[str] = []
        start_time: float = segments[0].start_seconds
        end_time: float = segments[0].end_seconds
        curr_words = 0
        chunk_idx = 0

        for seg in segments:
            seg_text = clean_text(seg.text)
            if not seg_text:
                continue

            words = seg_text.split()
            seg_sents = split_into_sentences(seg_text)

            # Check if adding this segment exceeds target window
            if curr_words + len(words) > self.chunk_size_tokens and curr_words >= self.min_chunk_words:
                combined_text = " ".join(curr_texts).strip()
                ts_str = f"{format_timestamp(start_time)} - {format_timestamp(end_time)}"
                chunks.append(
                    DocumentChunk(
                        chunk_id=f"{doc.doc_id}#chunk_{chunk_idx}",
                        doc_id=doc.doc_id,
                        file_name=doc.file_name,
                        modality="mp4",
                        text=combined_text,
                        sentences=curr_sents,
                        timestamp_str=ts_str,
                        start_seconds=start_time,
                        end_seconds=end_time,
                        word_count=curr_words,
                        chunk_index=chunk_idx
                    )
                )
                chunk_idx += 1
                curr_texts = [seg_text]
                curr_sents = seg_sents
                start_time = seg.start_seconds
                end_time = seg.end_seconds
                curr_words = len(words)
            else:
                curr_texts.append(seg_text)
                curr_sents.extend(seg_sents)
                end_time = seg.end_seconds
                curr_words += len(words)

        if curr_texts and curr_words >= self.min_chunk_words:
            combined_text = " ".join(curr_texts).strip()
            ts_str = f"{format_timestamp(start_time)} - {format_timestamp(end_time)}"
            chunks.append(
                DocumentChunk(
                    chunk_id=f"{doc.doc_id}#chunk_{chunk_idx}",
                    doc_id=doc.doc_id,
                    file_name=doc.file_name,
                    modality="mp4",
                    text=combined_text,
                    sentences=curr_sents,
                    timestamp_str=ts_str,
                    start_seconds=start_time,
                    end_seconds=end_time,
                    word_count=curr_words,
                    chunk_index=chunk_idx
                )
            )

        return chunks

    def _chunk_generic_text(
        self,
        doc_id: str,
        file_name: str,
        modality: str,
        raw_text: str,
        page_number: Optional[int] = None
    ) -> List[DocumentChunk]:
        """Chunks generic text string."""
        cleaned = clean_text(raw_text)
        sentences = split_into_sentences(cleaned)
        return self._slide_sentences(
            sentences=sentences,
            doc_id=doc_id,
            file_name=file_name,
            modality=modality,
            page_number=page_number,
            start_idx=0
        )

    def _slide_sentences(
        self,
        sentences: List[str],
        doc_id: str,
        file_name: str,
        modality: str,
        page_number: Optional[int],
        start_idx: int
    ) -> List[DocumentChunk]:
        """Slides a window over sentences maintaining target word counts and overlap."""
        chunks: List[DocumentChunk] = []
        if not sentences:
            return chunks

        idx = start_idx
        sent_idx = 0
        n_sents = len(sentences)

        while sent_idx < n_sents:
            current_sents: List[str] = []
            word_count = 0
            curr_pos = sent_idx

            while curr_pos < n_sents and word_count < self.chunk_size_tokens:
                sent = sentences[curr_pos]
                s_words = len(sent.split())
                current_sents.append(sent)
                word_count += s_words
                curr_pos += 1

            if current_sents and word_count >= self.min_chunk_words:
                chunk_text = " ".join(current_sents).strip()
                chunks.append(
                    DocumentChunk(
                        chunk_id=f"{doc_id}#p{page_number or 1}#c{idx}",
                        doc_id=doc_id,
                        file_name=file_name,
                        modality=modality,
                        text=chunk_text,
                        sentences=current_sents,
                        page_number=page_number,
                        word_count=word_count,
                        chunk_index=idx
                    )
                )
                idx += 1

            # Advance window with overlap
            # Calculate how many sentences correspond to chunk_overlap_tokens
            overlap_words = 0
            back_steps = 0
            while back_steps < len(current_sents) and overlap_words < self.chunk_overlap_tokens:
                overlap_words += len(current_sents[-(back_steps + 1)].split())
                back_steps += 1

            if curr_pos >= n_sents:
                break

            # Advance sent_idx
            advance = max(1, len(current_sents) - back_steps)
            sent_idx += advance

        return chunks
