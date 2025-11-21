from __future__ import annotations

import io
import re
import unicodedata
from typing import BinaryIO

from PyPDF2 import PdfReader

_PAGE_NUM_PATTERN = re.compile(r"^\s*\d+\s*$")
_WHITESPACE_PATTERN = re.compile(r"\s+")


def _clean_text(raw: str) -> str:
    normalized = unicodedata.normalize("NFKD", raw)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    lines = []
    for line in ascii_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if _PAGE_NUM_PATTERN.match(stripped):
            continue
        lines.append(stripped)
    collapsed = " ".join(lines)
    return _WHITESPACE_PATTERN.sub(" ", collapsed).strip()


def extract_text_from_pdf(pdf_file: BinaryIO | bytes) -> str:
    """
    Accepts an uploaded Streamlit file-like object or raw bytes and
    returns cleaned plain text.
    """
    try:
        if isinstance(pdf_file, bytes):
            buffer = io.BytesIO(pdf_file)
        else:
            buffer = pdf_file

        reader = PdfReader(buffer)
        raw_text = []
        for page in reader.pages:
            text = page.extract_text() or ""
            raw_text.append(text)
        combined = "\n".join(raw_text)
        return _clean_text(combined)
    except Exception as exc:  # pragma: no cover - defensive guardrail
        raise RuntimeError("Unable to extract text from PDF.") from exc

