from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


def generate_embedding(text: str) -> list[float]:
    embedding = model.encode(text)

    return embedding.tolist()


def embed_document_chunks(
    db: Session,
    document_id: int,
) -> int:

    chunks = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document_id)
        .all()
    )

    count = 0

    for chunk in chunks:

        embedding = generate_embedding(chunk.content)

        chunk.embedding = embedding

        count += 1

    db.commit()

    return count