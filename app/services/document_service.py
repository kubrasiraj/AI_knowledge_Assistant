from pathlib import Path

import pymupdf

from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.document_parser import extract_text


def split_text_into_chunks(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[str]:

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    return splitter.split_text(text)


def save_document_chunks(
    db: Session,
    document: Document,
    file_path: str,
) -> int:

    extension = Path(file_path).suffix.lower()

    total_chunks = 0

    if extension == ".pdf":

        pdf = pymupdf.open(file_path)

        try:
            for page_number, page in enumerate(pdf, start=1):

                page_text = page.get_text()

                if not page_text.strip():
                    continue

                chunks = split_text_into_chunks(page_text)

                for chunk in chunks:

                    document_chunk = DocumentChunk(
                        document_id=document.id,
                        chunk_index=total_chunks,
                        content=chunk,
                        page_number=page_number,
                    )

                    db.add(document_chunk)

                    total_chunks += 1

        finally:
            pdf.close()

    elif extension in {".txt", ".docx"}:

        text = extract_text(file_path)

        if text.strip():

            chunks = split_text_into_chunks(text)

            for chunk in chunks:

                document_chunk = DocumentChunk(
                    document_id=document.id,
                    chunk_index=total_chunks,
                    content=chunk,
                    page_number=None,
                )

                db.add(document_chunk)

                total_chunks += 1

    else:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    db.commit()

    return total_chunks