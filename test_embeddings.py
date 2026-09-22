from app.services.embedding_service import generate_embedding


text = "Artificial Intelligence is a field of computer science."
print("start")
embedding = generate_embedding(text)

print("Embedding generated successfully!")
print("Vector dimensions:", len(embedding))
print("First 5 values:", embedding[:5])