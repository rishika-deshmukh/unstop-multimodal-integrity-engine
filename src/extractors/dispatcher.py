"""
Extractors package dispatcher.
Routes input files to PDF, DOCX, or Video extractors based on file extension.
"""

from pathlib import Path
from typing import Optional

from src.extractors.base_extractor import BaseExtractor, ExtractedDocument
from src.extractors.pdf_extractor import PDFExtractor
from src.extractors.docx_extractor import DOCXExtractor
from src.extractors.video_extractor import VideoExtractor

class DocumentParser:
    def __init__(self, whisper_model: str = "base", device: str = "cpu"):
        self.pdf_extractor = PDFExtractor()
        self.docx_extractor = DOCXExtractor()
        self.video_extractor = VideoExtractor(model_name=whisper_model, device=device)

    def parse(self, file_path: Path) -> ExtractedDocument:
        file_path = Path(file_path)
        ext = file_path.suffix.lower()

        if ext == ".pdf":
            return self.pdf_extractor.extract(file_path)
        elif ext in (".docx", ".doc"):
            return self.docx_extractor.extract(file_path)
        elif ext in (".mp4", ".mkv", ".mov", ".avi", ".wav", ".mp3"):
            return self.video_extractor.extract(file_path)
        else:
            return ExtractedDocument(
                file_path=file_path,
                file_name=file_path.name,
                doc_id=file_path.name,
                modality="unknown",
                status="SKIPPED_CORRUPT",
                warning_message=f"Unsupported file format: {ext}"
            )
