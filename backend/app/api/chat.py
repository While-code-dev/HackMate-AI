from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Conversation, Message, User
from app.agent_core.orchestrator import MasterOrchestrator


router = APIRouter(
    prefix="/api",
    tags=["Chat"]
)

orchestrator = MasterOrchestrator()


class ChatRequest(BaseModel):
    user_message: str
    conversation_id: int | None = None


@router.post("/chat")
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # -------------------------------------------------
    # 1. Find existing conversation or create one
    # -------------------------------------------------

    if request.conversation_id is not None:

        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.id == request.conversation_id,
                Conversation.user_id == current_user.id
            )
            .first()
        )

        if conversation is None:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found"
            )

    else:

        conversation = Conversation(
            user_id=current_user.id
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)


    # -------------------------------------------------
    # 2. Load previous messages
    # -------------------------------------------------

    previous_messages = (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation.id
        )
        .order_by(Message.id)
        .all()
    )


    chat_history = [
        {
            "role": message.role,
            "content": message.content
        }
        for message in previous_messages
    ]


    # -------------------------------------------------
    # 3. Save user message
    # -------------------------------------------------

    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.user_message
    )

    db.add(user_message)
    db.commit()


    # -------------------------------------------------
    # 4. Send conversation history to AI
    # -------------------------------------------------

    result = orchestrator.process_message(
        user_message=request.user_message,
        history=chat_history
    )


    # -------------------------------------------------
    # 5. Save AI response
    # -------------------------------------------------

    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=result["chat_reply"]
    )

    db.add(assistant_message)
    db.commit()


    # -------------------------------------------------
    # 6. Return result
    # -------------------------------------------------

    return {
        "conversation_id": conversation.id,
        **result
    }

@router.get("/conversations")
def get_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conversations = (
        db.query(Conversation)
        .filter(
            Conversation.user_id == current_user.id
        )
        .order_by(Conversation.id.desc())
        .all()
    )

    return [
        {
            "conversation_id": conversation.id,
            "created_at": conversation.created_at
        }
        for conversation in conversations
    ]


@router.get("/conversations/{conversation_id}")
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
        .first()
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    messages = (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation.id
        )
        .order_by(Message.id)
        .all()
    )

    return {
        "conversation_id": conversation.id,
        "created_at": conversation.created_at,
        "messages": [
            {
                "id": message.id,
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at
            }
            for message in messages
        ]
    }