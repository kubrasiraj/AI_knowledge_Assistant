from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models.conversation import Conversation
from app.models.message import Message


def create_conversation(
    db: Session,
    user_id: int,
    title: str = "New Conversation",
) -> Conversation:

    conversation = Conversation(
        user_id=user_id,
        title=title,
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


def save_message(
    db: Session,
    conversation_id: int,
    role: str,
    content: str,
) -> Message:

    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
    )

    db.add(message)

    conversation = db.scalar(
        select(Conversation).where(
            Conversation.id == conversation_id,
        )
    )

    if conversation:
        conversation.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(message)

    return message


def get_user_conversations(
    db: Session,
    user_id: int,
) -> list[Conversation]:

    conversations = db.scalars(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    ).all()

    return list(conversations)


def get_conversation_messages(
    db: Session,
    conversation_id: int,
) -> list[Message]:

    messages = db.scalars(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    ).all()

    return list(messages)