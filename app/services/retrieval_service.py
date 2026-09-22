import numpy as np

from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.embedding_service import generate_embedding
from app.services.reranker_service import rerank_chunks


RERANK_SCORE_THRESHOLD = 0.0


def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:

    a = np.array(vector_a)
    b = np.array(vector_b)

    similarity = np.dot(a, b) / (
        np.linalg.norm(a) * np.linalg.norm(b)
    )

    return float(similarity)


def get_authorized_chunks(
    db: Session,
    document_id: int,
    user_id: int,
):
    return (
        db.query(DocumentChunk)
        .join(Document, Document.id == DocumentChunk.document_id)
        .filter(
            DocumentChunk.document_id == document_id,
            Document.user_id == user_id,
        )
        .all()
    )


def retrieve_relevant_chunks(
    db: Session,
    question: str,
    document_id: int,
    user_id: int,
    top_k: int = 5,
):

    query_embedding = generate_embedding(question)

    chunks = get_authorized_chunks(
        db=db,
        document_id=document_id,
        user_id=user_id,
    )

    results = []

    for chunk in chunks:

        if chunk.embedding is None:
            continue

        similarity = cosine_similarity(
            query_embedding,
            chunk.embedding,
        )

        results.append(
            {
                "chunk_id": chunk.id,
                "content": chunk.content,
                "page_number": chunk.page_number,
                "similarity": similarity,
            }
        )

    results.sort(
        key=lambda x: x["similarity"],
        reverse=True,
    )

    # First stage: retrieve more candidates
    candidates = results[:10]

    # Second stage: rerank candidates
    final_results = rerank_chunks(
        question=question,
        chunks=candidates,
        top_k=top_k,
    )

    # Evidence guard
    if not final_results:
        return []

    best_score = final_results[0]["rerank_score"]

    if best_score < RERANK_SCORE_THRESHOLD:
        return []

    return final_results