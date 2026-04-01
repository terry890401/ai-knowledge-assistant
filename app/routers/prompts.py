from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.schemas import PromptCreate, PromptResponse
from app.models import Prompt

router = APIRouter(prefix="/prompts", tags=["Prompt 管理"])

# 新增 prompt
@router.post("/", response_model=PromptResponse)
def create_prompt(
    prompt: PromptCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    new_prompt = Prompt(
        user_id=current_user.id,
        name=prompt.name,
        content=prompt.content,
        is_default=prompt.is_default
    )
    db.add(new_prompt)
    db.commit()
    db.refresh(new_prompt)
    return new_prompt

# 取得所有 prompt
@router.get("/", response_model=list[PromptResponse])
def get_prompts(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return db.query(Prompt).filter(Prompt.user_id == current_user.id).all()

# 刪除 prompt
@router.delete("/{prompt_id}", status_code=204)
def delete_prompt(
    prompt_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if prompt is None:
        raise HTTPException(status_code=404, detail="找不到該 Prompt")
    if prompt.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="無權限存取此 Prompt")
    db.delete(prompt)
    db.commit()