from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import ConversationCreate, ConversationResponse, ConversationDetailResponse
from app.database import get_db
from app.dependencies import get_current_user
from app.models import Conversation

router = APIRouter(prefix="/conversations", tags=["對話"])

# 新增對話
@router.post("/",response_model=ConversationResponse)
def create_conversation(
    conversation: ConversationCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    new_conversation = Conversation(title = conversation.title, user_id = current_user.id)
    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)

    return new_conversation

# 取得用戶所有對話
@router.get("/",response_model=list[ConversationResponse])
def get_conversation(
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    all_conversations = db.query(Conversation).filter(Conversation.user_id == current_user.id).all()
    
    return all_conversations

# 取得單一對話
@router.get("/{conversation_id}",response_model=ConversationDetailResponse)
def get_conversation_detail(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conversation is None:
        raise HTTPException(status_code=404, detail="找不到該對話")

    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403,detail="無權限存取此對話")
    
    return conversation