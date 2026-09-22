from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    document_id: int
    conversation_id: int | None = None


class SourceResponse(BaseModel):
    document_id: int
    filename: str
    chunk_id: int
    page_number: int | None


class ChatResponse(BaseModel):
    conversation_id: int
    answer: str
    sources: list[SourceResponse]