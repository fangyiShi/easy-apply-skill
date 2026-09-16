"""Small PDF inspection helpers with graceful fallbacks."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class PdfInspectionError(RuntimeError):
    pass


def page_count(pdf_path: str | Path) -> int:
    path = Path(pdf_path).resolve()
    if not path.is_file():
        raise PdfInspectionError(f"Missing PDF: {path}")

    try:
        from pypdf import PdfReader  # type: ignore

        return len(PdfReader(str(path)).pages)
    except ImportError:
        pass
    except Exception as exc:
        raise PdfInspectionError(f"Could not inspect {path} with pypdf: {exc}") from exc

    pdfinfo = shutil.which("pdfinfo")
    if pdfinfo:
        result = subprocess.run(
            [pdfinfo, str(path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if line.lower().startswith("pages:"):
                    return int(line.split(":", 1)[1].strip())
        raise PdfInspectionError(f"pdfinfo could not inspect {path}: {result.stderr.strip()}")

    raise PdfInspectionError(
        "Cannot determine PDF page count. Install `pypdf` or make `pdfinfo` available."
    )


def extract_text(pdf_path: str | Path) -> str:
    """Extract selectable text when a supported local method is available."""

    path = Path(pdf_path).resolve()
    try:
        from pypdf import PdfReader  # type: ignore

        parts = [(page.extract_text() or "") for page in PdfReader(str(path)).pages]
        return "\n".join(parts)
    except ImportError:
        pass
    except Exception as exc:
        raise PdfInspectionError(f"Could not extract text from {path}: {exc}") from exc

    pdftotext = shutil.which("pdftotext")
    if pdftotext:
        result = subprocess.run(
            [pdftotext, str(path), "-"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if result.returncode == 0:
            return result.stdout
        raise PdfInspectionError(f"pdftotext could not inspect {path}: {result.stderr.strip()}")

    raise PdfInspectionError(
        "Cannot extract PDF text. Install `pypdf` or make `pdftotext` available."
    )


def bottom_whitespace_ratio(pdf_path: str | Path) -> float | None:
    """Estimate trailing whitespace on the last page using PyMuPDF when available.

    Returns a ratio from 0 to 1, or ``None`` when PyMuPDF is unavailable or the
    page contains no positioned text blocks. This is a diagnostic, not a hard
    acceptance test.
    """

    try:
        import fitz  # type: ignore
    except ImportError:
        return None

    path = Path(pdf_path).resolve()
    try:
        document = fitz.open(str(path))
        if document.page_count == 0:
            return None
        page = document[-1]
        height = float(page.rect.height)
        blocks = page.get_text("blocks")
        if not blocks or height <= 0:
            return None
        lowest = max(float(block[3]) for block in blocks)
        ratio = max(0.0, min(1.0, (height - lowest) / height))
        return ratio
    except Exception:
        return None
