from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.document import Document
from app.models.conversation import Conversation
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag_service import generate_rag_answer

from app.models.conversation import Conversation
from app.services.conversation_service import get_conversation_messages
from app.services.conversation_service import (
    create_conversation,
    save_message,
    get_conversation_messages,
    get_user_conversations,
)


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post(
    "/",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Check document exists
    document = db.scalar(
        select(Document).where(
            Document.id == request.document_id,
        )
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # 2. Check document ownership
    if document.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this document",
        )

    print("DEBUG conversation_id:", request.conversation_id)

    if request.conversation_id in (None, 0):

        conversation = create_conversation(
        db=db,
        user_id=current_user.id,
        title=request.question[:50],
        )

        conversation_id = conversation.id

    else:

      conversation = db.scalar(
        select(Conversation).where(
            Conversation.id == request.conversation_id,
            Conversation.user_id == current_user.id,
        )
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    conversation_id = conversation.id

    # 5. Generate RAG answer
    

    rag_result = generate_rag_answer(
        db=db,
        question=request.question,
        document_id=request.document_id,
        user_id=current_user.id,
    )

    answer = rag_result["answer"]
    sources = rag_result["sources"]

    save_message(
        db=db,
        conversation_id=conversation_id,
        role="assistant",
        content=answer,
    )

    return ChatResponse(
        conversation_id=conversation_id,
        answer=answer,
        sources=sources,
    )


@router.get("/conversations")
def get_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversations = get_user_conversations(
        db=db,
        user_id=current_user.id,
    )

    return [
        {
            "id": conversation.id,
            "title": conversation.title,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
        }
        for conversation in conversations
    ]


@router.get("/conversations/{conversation_id}")
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = db.scalar(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    messages = get_conversation_messages(
        db=db,
        conversation_id=conversation_id,
    )

    return {
        "conversation_id": conversation.id,
        "user_id": conversation.user_id,
        "title": conversation.title,
        "messages": [
            {
                "id": message.id,
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at,
            }
            for message in messages
        ],
    }