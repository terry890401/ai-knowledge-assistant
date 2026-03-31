from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import ConversationCreate, ConversationResponse, ConversationDetailResponse, ChatRequest, MessageResponse
from app.database import get_db
from app.dependencies import get_current_user
from app.models import Conversation, Message
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

# 刪除對話
@router.delete("/{conversation_id}",status_code=204)
def del_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    conversation = conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()

    if conversation is None:
        raise HTTPException(status_code=404, detail="找不到該對話")
    
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403,detail="無權限存取此對話")
    
    db.delete(conversation)
    db.commit()

@router.post("/{conversation_id}/chat", response_model=MessageResponse)
def chat(
    conversation_id: int,
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()

    if conversation is None:
        raise HTTPException(status_code=404, detail="找不到該對話")
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="無權限存取此對話")
    
    user_message = Message(
        conversation_id = conversation_id,
        role = "user",
        content = request.content
    )

    db.add(user_message)
    db.commit()
    db.refresh(user_message)

    history = db.query(Message).filter(Message.conversation_id == conversation_id).all()
    messages = [{"role": "system", "content": "你是一個友善的助手，用繁體中文回答"}]
    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    ai_reply = response.choices[0].message.content

    ai_message = Message(
        conversation_id = conversation_id,
        role = "assistant",
        content = ai_reply
    )
    db.add(ai_message)
    db.commit()
    db.refresh(ai_message)

    return ai_message