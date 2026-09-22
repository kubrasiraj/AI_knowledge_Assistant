from app.services.context_service import build_context


chunks = [
    {
        "chunk_id": 103,
        "page_number": 25,
        "content": "Artificial Intelligence is a field that focuses on creating intelligent systems.",
    },
    {
        "chunk_id": 80,
        "page_number": 2,
        "content": "Artificial Intelligence can be used for recommendation systems and natural language processing.",
    },
]


context = build_context(chunks)


print("===== BUILT CONTEXT =====")
print(context)