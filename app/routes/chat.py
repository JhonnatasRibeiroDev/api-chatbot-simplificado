from fastapi import APIRouter, HTTPException, status

from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.services.llm_service import generate_answer
from app.services.session_service import add_message_to_history, get_history_by_session

router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"]
)

@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
def send_message(request: ChatRequest):
    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A mensagem não pode estar vazia"
        )

    try:
        add_message_to_history(
            session_id=request.session_id,
            role="user",
            content=message
        )

        history = get_history_by_session(request.session_id)
        chatbot_response = generate_answer(message=message, history=history)

        add_message_to_history(
            session_id=request.session_id,
            role="assistant",
            content=chatbot_response
        )

        return ChatResponse(
            session_id=request.session_id,
            response=chatbot_response
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )
