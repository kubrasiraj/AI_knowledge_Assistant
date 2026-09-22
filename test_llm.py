from app.services.llm_service import generate_answer


prompt = """
You are a helpful AI assistant.

Explain what Artificial Intelligence is in simple terms.
"""


answer = generate_answer(prompt)


print("===== LLM RESPONSE =====")
print(answer)