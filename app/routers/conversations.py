from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas import ConversationCreate, ConversationResponse
from app.database import get_db
from app.dependencies import get_current_user
from app.models import Conversation

router = APIRouter(prefix="/conversations", tags=["對話"])

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