"""
PDF document extractor using pypdf.
Extracts text page-by-page, preserves page-level metadata,
and handles zero-byte, corrupted, or encrypted files gracefully.
"""

import os
import logging
from pathlib import Path
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from src.extractors.base_extractor import BaseExtractor, ExtractedDocument, PageContent

logger = logging.getLogger("pdf_extractor")

class PDFExtractor(BaseExtractor):
    def extract(self, file_path: Path) -> ExtractedDocument:
        file_path = Path(file_path)
        file_name = file_path.name
        doc_id = file_name

        # 1. Zero-byte or non-existent file check
        if not file_path.exists():
            logger.warning(f"[PDF] File does not exist: {file_path}")
            return ExtractedDocument(
                file_path=file_path,
                file_name=file_name,
                doc_id=doc_id,
                modality="pdf",
                status="SKIPPED_CORRUPT",
                warning_message=f"File not found: {file_name}"
            )

        file_size = os.path.getsize(file_path)
        if file_size == 0:
            logger.warning(f"[PDF] Zero-byte PDF detected: {file_name}. Gracefully skipping.")
            return ExtractedDocument(
                file_path=file_path,
                file_name=file_name,
                doc_id=doc_id,
                modality="pdf",
                status="SKIPPED_EMPTY",
                warning_message=f"Zero-byte empty PDF submission: {file_name}"
            )

        # 2. Parse PDF pages with try/except
        try:
            reader = PdfReader(str(file_path))
            
            if reader.is_encrypted:
                try:
                    # Attempt empty password decryption
                    reader.decrypt("")
                except Exception:
                    logger.warning(f"[PDF] Password-protected/encrypted PDF: {file_name}")
                    return ExtractedDocument(
                        file_path=file_path,
                        file_name=file_name,
                        doc_id=doc_id,
                        modality="pdf",
                        status="SKIPPED_CORRUPT",
                        warning_message=f"Encrypted/password-protected PDF: {file_name}"
                    )

            pages_content: list[PageContent] = []
            full_text_parts: list[str] = []

            for idx, page in enumerate(reader.pages, start=1):
                page_text = page.extract_text() or ""
                # Basic cleaning: normalize carriage returns
                cleaned_page_text = page_text.replace("\r\n", "\n").replace("\r", "\n").strip()
                if cleaned_page_text:
                    pages_content.append(PageContent(page_number=idx, text=cleaned_page_text))
                    full_text_parts.append(cleaned_page_text)

            total_text = "\n\n".join(full_text_parts).strip()

            if not total_text:
                logger.warning(f"[PDF] PDF contains 0 extractable text characters: {file_name}")
                return ExtractedDocument(
                    file_path=file_path,
                    file_name=file_name,
                    doc_id=doc_id,
                    modality="pdf",
                    pages=pages_content,
                    raw_text="",
                    status="SKIPPED_EMPTY",
                    warning_message=f"No extractable text found in PDF: {file_name} (scanned/blank document)"
                )

            return ExtractedDocument(
                file_path=file_path,
                file_name=file_name,
                doc_id=doc_id,
                modality="pdf",
                raw_text=total_text,
                pages=pages_content,
                status="SUCCESS"
            )

        except (PdfReadError, Exception) as e:
            logger.warning(f"[PDF] Corrupt or unreadable PDF: {file_name}. Error: {e}")
            return ExtractedDocument(
                file_path=file_path,
                file_name=file_name,
                doc_id=doc_id,
                modality="pdf",
                status="SKIPPED_CORRUPT",
                warning_message=f"Corrupt or malformed PDF: {e}"
            )
