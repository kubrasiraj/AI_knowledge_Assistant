from sqlalchemy.orm import Session

from app.models.document import Document
from app.services.retrieval_service import retrieve_relevant_chunks
from app.services.context_service import build_context
from app.services.prompt_service import build_rag_prompt
from app.services.llm_service import generate_answer


def generate_rag_answer(
    db: Session,
    question: str,
    document_id: int,
    user_id: int,
) -> dict:

    chunks = retrieve_relevant_chunks(
        db=db,
        question=question,
        document_id=document_id,
        user_id=user_id,
        top_k=5,
    )

    if not chunks:
        return {
            "answer": "I don't have enough information in the provided documents.",
            "sources": [],
        }

    context = build_context(chunks)

    prompt = build_rag_prompt(
        question=question,
        context=context,
    )

    answer = generate_answer(prompt)

    sources = [
        {
                "document_id": document_id,
                "filename": db.get(Document, document_id).filename,
                "chunk_id": chunk["chunk_id"],
                "page_number": chunk["page_number"],
            }
    
            for chunk in chunks
    ]

    return {
        "answer": answer,
        "sources": sources,
    }