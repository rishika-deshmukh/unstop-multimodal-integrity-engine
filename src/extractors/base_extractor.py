"""
Base extractor interfaces and data classes for multi-modal submission parsing.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

@dataclass
class PageContent:
    page_number: int  # 1-indexed
    text: str

@dataclass
class AudioSegment:
    start_seconds: float
    end_seconds: float
    timestamp_str: str  # Format: "HH:MM:SS - HH:MM:SS"
    text: str
    no_speech_prob: float = 0.0

@dataclass
class ExtractedDocument:
    file_path: Path
    file_name: str
    doc_id: str
    modality: str  # 'pdf', 'docx', 'mp4'
    raw_text: str = ""
    pages: List[PageContent] = field(default_factory=list)
    audio_segments: List[AudioSegment] = field(default_factory=list)
    paragraphs: List[str] = field(default_factory=list)
    status: str = "SUCCESS"  # SUCCESS, WARNING, SKIPPED_EMPTY, SKIPPED_CORRUPT, SKIPPED_SILENT
    warning_message: Optional[str] = None

    @property
    def is_usable(self) -> bool:
        return self.status in ("SUCCESS", "WARNING") and len(self.raw_text.strip()) > 0

class BaseExtractor:
    """Base class for document extractors across all formats."""
    def extract(self, file_path: Path) -> ExtractedDocument:
        raise NotImplementedError
