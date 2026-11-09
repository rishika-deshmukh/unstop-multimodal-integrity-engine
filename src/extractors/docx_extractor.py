"""
DOCX document extractor using python-docx.
Extracts paragraphs and tables, preserves structure,
and handles empty or corrupt files gracefully without crashing.
"""

import os
import logging
from pathlib import Path
from docx import Document
from docx.opc.exceptions import PackageNotFoundError

from src.extractors.base_extractor import BaseExtractor, ExtractedDocument

logger = logging.getLogger("docx_extractor")

class DOCXExtractor(BaseExtractor):
    def extract(self, file_path: Path) -> ExtractedDocument:
        file_path = Path(file_path)
        file_name = file_path.name
        doc_id = file_name

        if not file_path.exists():
            logger.warning(f"[DOCX] File does not exist: {file_path}")
            return ExtractedDocument(
                file_path=file_path,
                file_name=file_name,
                doc_id=doc_id,
                modality="docx",
                status="SKIPPED_CORRUPT",
                warning_message=f"File not found: {file_name}"
            )

        file_size = os.path.getsize(file_path)
        if file_size == 0:
            logger.warning(f"[DOCX] Zero-byte DOCX detected: {file_name}. Gracefully skipping.")
            return ExtractedDocument(
                file_path=file_path,
                file_name=file_name,
                doc_id=doc_id,
                modality="docx",
                status="SKIPPED_EMPTY",
                warning_message=f"Zero-byte empty DOCX submission: {file_name}"
            )

        try:
            doc = Document(str(file_path))
            paragraphs: list[str] = []

            # Extract body paragraphs
            for p in doc.paragraphs:
                text = p.text.strip()
                if text:
                    paragraphs.append(text)

            # Extract table cells as well
            for table in doc.tables:
                for row in table.rows:
                    row_texts = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if row_texts:
                        paragraphs.append(" | ".join(row_texts))

            total_text = "\n\n".join(paragraphs).strip()

            if not total_text:
                logger.warning(f"[DOCX] No extractable text in DOCX: {file_name}")
                return ExtractedDocument(
                    file_path=file_path,
                    file_name=file_name,
                    doc_id=doc_id,
                    modality="docx",
                    raw_text="",
                    paragraphs=paragraphs,
                    status="SKIPPED_EMPTY",
                    warning_message=f"No extractable text found in DOCX: {file_name}"
                )

            return ExtractedDocument(
                file_path=file_path,
                file_name=file_name,
                doc_id=doc_id,
                modality="docx",
                raw_text=total_text,
                paragraphs=paragraphs,
                status="SUCCESS"
            )

        except (PackageNotFoundError, Exception) as e:
            logger.warning(f"[DOCX] Corrupt or unreadable DOCX: {file_name}. Error: {e}")
            return ExtractedDocument(
                file_path=file_path,
                file_name=file_name,
                doc_id=doc_id,
                modality="docx",
                status="SKIPPED_CORRUPT",
                warning_message=f"Corrupt or malformed DOCX: {e}"
            )
