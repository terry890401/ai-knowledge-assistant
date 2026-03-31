from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.schemas import DocumentResponse
from app.models import Document
from app.vector_store import add_document

router = APIRouter(prefix="/documents", tags=["文件"])

@router.post("/", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # 讀取文件內容
    content = await file.read()
    text = content.decode("utf-8")

    document = Document(
        user_id = current_user.id,
        filename = file.filename,
        content = text
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    add_document(document.id, text)

    return document