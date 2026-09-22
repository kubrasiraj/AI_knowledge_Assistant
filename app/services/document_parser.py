from pathlib import Path

import fitz
from docx import Document


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from all pages of a PDF file.
    """

    pdf_document = fitz.open(file_path)

    pages = []

    try:
        for page in pdf_document:
            text = page.get_text()

            if text.strip():
                pages.append(text.strip())

    finally:
        pdf_document.close()

    return "\n\n".join(pages)


def extract_text_from_txt(file_path: str) -> str:
    """
    Extract text from a TXT file.
    """

    path = Path(file_path)

    return path.read_text(
        encoding="utf-8",
        errors="ignore",
    ).strip()


def extract_text_from_docx(file_path: str) -> str:
    """
    Extract text from paragraphs of a DOCX file.
    """

    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    return "\n\n".join(paragraphs)


def extract_text(file_path: str) -> str:
    """
    Detect the file type and extract its text.
    """

    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":
        return extract_text_from_pdf(file_path)

    if extension == ".txt":
        return extract_text_from_txt(file_path)

    if extension == ".docx":
        return extract_text_from_docx(file_path)

    raise ValueError(
        f"Unsupported file type: {extension}"
    )