
from pathlib import Path

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    UploadFile,
)
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.core.log import logger
from app.models.document import Document
from app.models.user import User
from app.services.document_parser import extract_text
from app.services.document_service import save_document_chunks
from app.services.embedding_service import embed_document_chunks


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".docx",
}


def process_document(document_id: int):
    """
    Process the uploaded document in the background.
    """

    db = get_db()

    try:
        document = db.query(Document).filter(
            Document.id == document_id
        ).first()

        if not document:
            logger.warning(
                "Document not found | document_id=%s",
                document_id,
            )
            return

        document.status = "processing"
        db.commit()

        logger.info(
            "Document processing started | document_id=%s | filename=%s",
            document.id,
            document.filename,
        )

        extract_text(
            document.file_path
        )

        logger.info(
            "Text extraction completed | document_id=%s",
            document.id,
        )

        save_document_chunks(
            db=db,
            document=document,
            file_path=document.file_path,
        )

        logger.info(
            "Document chunking completed | document_id=%s",
            document.id,
        )

        embed_document_chunks(
            db=db,
            document_id=document.id,
        )

        logger.info(
            "Document embeddings completed | document_id=%s",
            document.id,
        )

        document.status = "completed"
        db.commit()

        logger.info(
            "Document processing completed | document_id=%s",
            document.id,
        )

    except Exception:
        db.rollback()

        document = db.query(Document).filter(
            Document.id == document_id
        ).first()

        if document:
            document.status = "failed"
            db.commit()

        logger.exception(
            "Document processing failed | document_id=%s",
            document_id,
        )

    finally:
        db.close()


@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    if not file.filename:
        logger.warning(
            "Upload rejected | filename missing | user_id=%s",
            current_user.id,
        )

        raise HTTPException(
            status_code=400,
            detail="Filename is required",
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        logger.warning(
            "Upload rejected | unsupported extension=%s | user_id=%s",
            extension,
            current_user.id,
        )

        raise HTTPException(
            status_code=400,
            detail="Only PDF, TXT, and DOCX files are supported",
        )

    logger.info(
        "Document upload started | user_id=%s | filename=%s",
        current_user.id,
        file.filename,
    )

    file_path = UPLOAD_DIR / file.filename

    content = await file.read()

    with open(file_path, "wb") as buffer:
        buffer.write(content)

    document = Document(
        user_id=current_user.id,
        filename=file.filename,
        file_path=str(file_path),
        status="uploaded",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    logger.info(
        "Document record created | document_id=%s | user_id=%s",
        document.id,
        current_user.id,
    )

    background_tasks.add_task(
        process_document,
        document.id,
    )

    logger.info(
        "Background processing scheduled | document_id=%s",
        document.id,
    )

    return {
        "message": "Document uploaded successfully",
        "document_id": document.id,
        "user_id": current_user.id,
        "filename": file.filename,
        "file_type": extension,
        "status": document.status,
    }


@router.get("/")
async def get_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    documents = db.query(Document).filter(
        Document.user_id == current_user.id
    ).all()

    logger.info(
        "Documents fetched | user_id=%s | count=%s",
        current_user.id,
        len(documents),
    )

    return {
        "documents": [
            {
                "document_id": document.id,
                "filename": document.filename,
                "status": document.status,
                "created_at": document.created_at,
            }
            for document in documents
        ]
    }


@router.get("/{document_id}")
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id,
    ).first()

    if not document:
        logger.warning(
            "Document not found | document_id=%s | user_id=%s",
            document_id,
            current_user.id,
        )

        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    logger.info(
        "Document fetched | document_id=%s | user_id=%s",
        document_id,
        current_user.id,
    )

    return {
        "document_id": document.id,
        "user_id": document.user_id,
        "filename": document.filename,
        "file_type": Path(document.filename).suffix.lower(),
        "status": document.status,
        "created_at": document.created_at,
    }


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id,
    ).first()

    if not document:
        logger.warning(
            "Delete failed | document not found | document_id=%s | user_id=%s",
            document_id,
            current_user.id,
        )

        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    file_path = Path(document.file_path)

    if file_path.exists():
        file_path.unlink()

    db.delete(document)
    db.commit()

    logger.info(
        "Document deleted | document_id=%s | user_id=%s",
        document_id,
        current_user.id,
    )

    return {
        "message": "Document deleted successfully",
        "document_id": document_id,
    }

