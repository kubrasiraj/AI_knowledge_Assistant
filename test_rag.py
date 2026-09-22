from app.db.database import SessionLocal
from app.services.rag_service import generate_rag_answer


db = SessionLocal()


question = "What is this project about?"


answer = generate_rag_answer(
    db=db,
    question=question,
    document_id=5,
    user_id=5,
)


print("===== RAG ANSWER =====")
print(answer)


db.close()