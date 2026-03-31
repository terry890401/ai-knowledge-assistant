from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.schemas import ConversationCreate, ConversationResponse, ConversationDetailResponse, ChatRequest, MessageResponse
from app.database import get_db
from app.dependencies import get_current_user
from app import models
from app.models import Conversation, Message, Document
from app.vector_store import search_documents
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

router = APIRouter(prefix="/conversations", tags=["對話"])

def generate(response, conversation_id, db):
    full_reply = ""
    for chunk in response:
        delta = chunk.choices[0].delta.content
        if delta:
            full_reply += delta
            yield f"data: {delta}\n\n"

    ai_message = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=full_reply
    )
    db.add(ai_message)
    db.commit()
    yield "data: [DONE]\n\n"

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

# 聊天
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

    # 取得對話歷史
    history = db.query(Message).filter(Message.conversation_id == conversation_id).all()

    # 搜尋用戶文件的相關段落
    user_docs = db.query(Document).filter(Document.user_id == current_user.id).all()
    user_doc_ids = [doc.id for doc in user_docs]
    relevant_docs = search_documents(request.content, user_doc_ids)

    # 組成 system prompt（有相關文件就加進去）
    system_prompt = "你是一個友善的助手，用繁體中文回答"
    if relevant_docs:
        context = "\n\n".join(relevant_docs)
        system_prompt += f"\n\n根據以下資料回答問題，如果資料中有答案請優先使用：\n{context}"

    # 組成 messages
    messages = [{"role": "system", "content": system_prompt}]
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

# 聊天 stream
@router.post("/{conversation_id}/chat/stream")
def chat_stream(
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
        messages=messages,
        stream = True
    )

    return StreamingResponse(
        generate(response, conversation_id, db),
        media_type="text/event-stream"
    )