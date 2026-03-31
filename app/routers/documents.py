from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.schemas import DocumentResponse
from app.models import Document
from app.vector_store import add_document, delete_document

router = APIRouter(prefix="/documents", tags=["文件"])

# 上傳文件
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

# 取得文件
@router.get("/",response_model=list[DocumentResponse])
def get_dcouments(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    document = db.query(Document).filter(Document.user_id == current_user.id).all()

    return document

# 刪除文件
@router.delete("/{document_id}", status_code=204)
def del_documents(
    document_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    document = db.query(Document).filter(Document.id == document_id).first()

    if document is None:
        raise HTTPException(status_code=404, detail="找不到該對話")
    
    if document.user_id != current_user.id:
        raise HTTPException(status_code=403,detail="無權限存取此對話")
    
    db.delete(document)
    db.commit()

    delete_document(document_id)