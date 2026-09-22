
from pathlib import Path

import app.routers.documents as documents_router


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


def test_upload_txt_document(client, monkeypatch):
    token = register_and_login(
        client,
        "Document User",
        "document@example.com",
    )

    # Do not run the real background processing during this API test.
    monkeypatch.setattr(
        documents_router,
        "process_document",
        lambda document_id: None,
    )

    response = client.post(
        "/documents/upload",
        headers={
            "Authorization": f"Bearer {token}"
        },
        files={
            "file": (
                "test.txt",
                b"This is a test document.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Document uploaded successfully"
    assert data["filename"] == "test.txt"
    assert data["file_type"] == ".txt"
    assert data["status"] == "uploaded"
    assert "document_id" in data

    # Clean up uploaded file.
    file_path = Path("uploads/test.txt")

    if file_path.exists():
        file_path.unlink()


def test_get_documents(client, monkeypatch):
    token = register_and_login(
        client,
        "List User",
        "list@example.com",
    )

    monkeypatch.setattr(
        documents_router,
        "process_document",
        lambda document_id: None,
    )

    client.post(
        "/documents/upload",
        headers={
            "Authorization": f"Bearer {token}"
        },
        files={
            "file": (
                "list-test.txt",
                b"Document for list testing.",
                "text/plain",
            )
        },
    )

    response = client.get(
        "/documents/",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "documents" in data
    assert len(data["documents"]) == 1
    assert data["documents"][0]["filename"] == "list-test.txt"

    file_path = Path("uploads/list-test.txt")

    if file_path.exists():
        file_path.unlink()


def test_get_single_document(client, monkeypatch):
    token = register_and_login(
        client,
        "Single User",
        "single@example.com",
    )

    monkeypatch.setattr(
        documents_router,
        "process_document",
        lambda document_id: None,
    )

    upload_response = client.post(
        "/documents/upload",
        headers={
            "Authorization": f"Bearer {token}"
        },
        files={
            "file": (
                "single-test.txt",
                b"Single document test.",
                "text/plain",
            )
        },
    )

    document_id = upload_response.json()["document_id"]

    response = client.get(
        f"/documents/{document_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["document_id"] == document_id
    assert data["filename"] == "single-test.txt"
    assert data["file_type"] == ".txt"

    file_path = Path("uploads/single-test.txt")

    if file_path.exists():
        file_path.unlink()


def test_upload_invalid_file_type(client):
    token = register_and_login(
        client,
        "File User",
        "file@example.com",
    )

    response = client.post(
        "/documents/upload",
        headers={
            "Authorization": f"Bearer {token}"
        },
        files={
            "file": (
                "malicious.exe",
                b"fake executable content",
                "application/octet-stream",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["message"] == (
        "Only PDF, TXT, and DOCX files are supported"
    )


def test_user_cannot_access_another_users_document(
    client,
    monkeypatch,
):
    user1_token = register_and_login(
        client,
        "User One",
        "user1@example.com",
    )

    user2_token = register_and_login(
        client,
        "User Two",
        "user2@example.com",
    )

    monkeypatch.setattr(
        documents_router,
        "process_document",
        lambda document_id: None,
    )

    upload_response = client.post(
        "/documents/upload",
        headers={
            "Authorization": f"Bearer {user1_token}"
        },
        files={
            "file": (
                "private.txt",
                b"Private document.",
                "text/plain",
            )
        },
    )

    document_id = upload_response.json()["document_id"]

    response = client.get(
        f"/documents/{document_id}",
        headers={
            "Authorization": f"Bearer {user2_token}"
        },
    )

    assert response.status_code == 404
    assert response.json()["message"] == "Document not found"

    file_path = Path("uploads/private.txt")

    if file_path.exists():
        file_path.unlink()


def test_delete_document(client, monkeypatch):
    token = register_and_login(
        client,
        "Delete User",
        "delete@example.com",
    )

    monkeypatch.setattr(
        documents_router,
        "process_document",
        lambda document_id: None,
    )

    upload_response = client.post(
        "/documents/upload",
        headers={
            "Authorization": f"Bearer {token}"
        },
        files={
            "file": (
                "delete-test.txt",
                b"Document to delete.",
                "text/plain",
            )
        },
    )

    document_id = upload_response.json()["document_id"]

    response = client.delete(
        f"/documents/{document_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Document deleted successfully"
    assert data["document_id"] == document_id

    # Verify the document is no longer accessible.
    get_response = client.get(
        f"/documents/{document_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert get_response.status_code == 404
