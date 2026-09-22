from app.services.reranker_service import rerank_chunks


question = "What is Artificial Intelligence?"

chunks = [
    {
        "chunk_id": 1,
        "content": "Artificial Intelligence is a field of computer science that focuses on creating systems capable of performing tasks that normally require human intelligence.",
    },
    {
        "chunk_id": 2,
        "content": "The weather today is sunny and the temperature is high.",
    },
    {
        "chunk_id": 3,
        "content": "Artificial Intelligence can be used in recommendation systems, natural language processing, and computer vision.",
    },
]


results = rerank_chunks(
    question=question,
    chunks=chunks,
    top_k=3,
)


for result in results:
    print("\n--- RESULT ---")
    print("Chunk ID:", result["chunk_id"])
    print("Rerank Score:", result["rerank_score"])
    print("Content:", result["content"])