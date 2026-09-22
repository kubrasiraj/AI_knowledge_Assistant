from app.db.database import SessionLocal
from app.services.retrieval_service import retrieve_relevant_chunks


db = SessionLocal()

results = retrieve_relevant_chunks(
    db=db,
    question="What is Artificial Intelligence?",
    document_id=5,
    user_id=5,
    top_k=5,
)

if not results:
    print("No relevant chunks found.")
else:
    print("Total results:", len(results))

    for result in results:
        print("\n--- RESULT ---")
        print("Chunk ID:", result["chunk_id"])
        print("Page:", result["page_number"])
        print("Similarity:", result["similarity"])
        print("Rerank Score:", result["rerank_score"])
        print("Content:", result["content"])

db.close()
