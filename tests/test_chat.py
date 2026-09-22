
from pathlib import Path

import app.routers.chat as chat_router


def register_and_login(
    client,
    name,
    email,
    password="123456",
):
    register_response = client.post(
        "/auth/register",
        json={
            "name": name,
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 200

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    return login_response.json()["access_token"]


def upload_test_document(client, token, filename="chat-test.txt"):
    response = client.post(
        "/documents/upload",
        headers={
            "Authorization": f"Bearer {token}"
        },
        files={
            "file": (
                filename,
                b"This is a test document for chat.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 200

    return response.json()["document_id"]


def test_chat_with_document(client, monkeypatch):
    token = register_and_login(
        client,
        "Chat User",
        "chat@example.com",
    )

    # Prevent real document processing.
    import app.routers.documents as documents_router

    monkeypatch.setattr(
        documents_router,
        "process_document",
        lambda document_id: None,
    )

    document_id = upload_test_document(
        client,
        token,
    )

    # Mock the real RAG/LLM pipeline.
    monkeypatch.setattr(
        chat_router,
        "generate_rag_answer",
        lambda **kwargs: {
            "answer": "This is a grounded test answer.",
            "sources": [
                {
                    "document_id": document_id,
                    "filename": "chat-test.txt",
                    "chunk_id": 1,
                    "page_number": None,
                }
            ],
        },
    )

    response = client.post(
        "/chat/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "document_id": document_id,
            "question": "What is in this document?",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["answer"] == "This is a grounded test answer."
    assert data["conversation_id"] is not None
    assert len(data["sources"]) == 1

    file_path = Path("uploads/chat-test.txt")

    if file_path.exists():
        file_path.unlink()


def test_chat_document_not_found(client):
    token = register_and_login(
        client,
        "Missing Document User",
        "missing-document@example.com",
    )

    response = client.post(
        "/chat/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "document_id": 99999,
            "question": "What is this?",
        },
    )

    assert response.status_code == 404
    assert response.json()["message"] == "Document not found"


def test_chat_cannot_access_another_users_document(
    client,
    monkeypatch,
):
    user1_token = register_and_login(
        client,
        "Chat User One",
        "chat-user1@example.com",
    )

    user2_token = register_and_login(
        client,
        "Chat User Two",
        "chat-user2@example.com",
    )

    import app.routers.documents as documents_router

    monkeypatch.setattr(
        documents_router,
        "process_document",
        lambda document_id: None,
    )

    document_id = upload_test_document(
        client,
        user1_token,
        "private-chat.txt",
    )

    response = client.post(
        "/chat/",
        headers={
            "Authorization": f"Bearer {user2_token}"
        },
        json={
            "document_id": document_id,
            "question": "Can I access this?",
        },
    )

    assert response.status_code == 403
    assert response.json()["message"] == (
        "You do not have access to this document"
    )

    file_path = Path("uploads/private-chat.txt")

    if file_path.exists():
        file_path.unlink()


def test_chat_creates_new_conversation(
    client,
    monkeypatch,
):
    token = register_and_login(
        client,
        "New Conversation User",
        "new-conversation@example.com",
    )

    import app.routers.documents as documents_router

    monkeypatch.setattr(
        documents_router,
        "process_document",
        lambda document_id: None,
    )

    document_id = upload_test_document(
        client,
        token,
        "new-conversation.txt",
    )

    monkeypatch.setattr(
        chat_router,
        "generate_rag_answer",
        lambda **kwargs: {
            "answer": "Test answer",
            "sources": [],
        },
    )

    response = client.post(
        "/chat/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "document_id": document_id,
            "question": "First question",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["conversation_id"] is not None

    file_path = Path("uploads/new-conversation.txt")

    if file_path.exists():
        file_path.unlink()


def test_get_user_conversations(
    client,
    monkeypatch,
):
    token = register_and_login(
        client,
        "Conversation List User",
        "conversation-list@example.com",
    )

    import app.routers.documents as documents_router

    monkeypatch.setattr(
        documents_router,
        "process_document",
        lambda document_id: None,
    )

    document_id = upload_test_document(
        client,
        token,
        "conversation-list.txt",
    )

    monkeypatch.setattr(
        chat_router,
        "generate_rag_answer",
        lambda **kwargs: {
            "answer": "Conversation answer",
            "sources": [],
        },
    )

    chat_response = client.post(
        "/chat/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "document_id": document_id,
            "question": "Create a conversation",
        },
    )

    assert chat_response.status_code == 200

    response = client.get(
        "/chat/conversations",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["title"] == "Create a conversation"

    file_path = Path("uploads/conversation-list.txt")

    if file_path.exists():
        file_path.unlink()


def test_get_conversation_cannot_access_another_users_conversation(
    client,
    monkeypatch,
):
    user1_token = register_and_login(
        client,
        "Conversation Owner",
        "conversation-owner@example.com",
    )

    user2_token = register_and_login(
        client,
        "Conversation Other User",
        "conversation-other@example.com",
    )

    import app.routers.documents as documents_router

    monkeypatch.setattr(
        documents_router,
        "process_document",
        lambda document_id: None,
    )

    document_id = upload_test_document(
        client,
        user1_token,
        "conversation-private.txt",
    )

    monkeypatch.setattr(
        chat_router,
        "generate_rag_answer",
        lambda **kwargs: {
            "answer": "Private conversation answer",
            "sources": [],
        },
    )

    chat_response = client.post(
        "/chat/",
        headers={
            "Authorization": f"Bearer {user1_token}"
        },
        json={
            "document_id": document_id,
            "question": "Private question",
        },
    )

    conversation_id = chat_response.json()["conversation_id"]

    response = client.get(
        f"/chat/conversations/{conversation_id}",
        headers={
            "Authorization": f"Bearer {user2_token}"
        },
    )

    assert response.status_code == 404
    assert response.json()["message"] == "Conversation not found"

    file_path = Path("uploads/conversation-private.txt")

    if file_path.exists():
        file_path.unlink()

