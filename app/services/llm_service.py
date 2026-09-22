from groq import Groq

from app.core.config import settings


MODEL_NAME = "openai/gpt-oss-120b"

client = Groq(
    api_key=settings.groq_api_key,
)


def generate_answer(prompt: str) -> str:

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response.choices[0].message.content