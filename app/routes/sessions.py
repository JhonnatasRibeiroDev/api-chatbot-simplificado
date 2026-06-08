from fastapi import APIRouter, Body, Cookie, HTTPException, Response, status

from app.schemas.chat_schema import ChatMessageRequest, ChatResponse
from app.schemas.session_schema import (
    ClientSessionsResponse,
    SessionRequest,
    SessionHistoryResponse,
    SessionResponse,
)
from app.services.llm_service import generate_answer
from app.services.session_service import (
    add_message_to_history,
    create_session,
    get_history_by_session,
    list_sessions_by_client,
)


router = APIRouter(
    prefix="/api/sessions",
    tags=["Sessions"]
)

CLIENT_ID_COOKIE_NAME = "client_id"
CLIENT_ID_COOKIE_MAX_AGE_SECONDS = 60 * 60 * 24 * 365


@router.post("", response_model=SessionResponse)
def create_new_session(
    response: Response,
    request: SessionRequest | None = Body(default=None),
    client_id_cookie: str | None = Cookie(default=None, alias=CLIENT_ID_COOKIE_NAME),
):
    client_id = request.client_id if request and request.client_id else client_id_cookie
    session = create_session(client_id=client_id)
    response.set_cookie(
        key=CLIENT_ID_COOKIE_NAME,
        value=session["client_id"],
        max_age=CLIENT_ID_COOKIE_MAX_AGE_SECONDS,
        httponly=True,
        samesite="lax",
    )

    return SessionResponse(
        client_id=session["client_id"],
        session_id=session["session_id"]
    )


@router.get("/clients/{client_id}", response_model=ClientSessionsResponse)
def get_client_sessions(client_id: str):
    sessions = list_sessions_by_client(client_id)

    return ClientSessionsResponse(
        client_id=client_id,
        sessions=sessions
    )


@router.get("/me", response_model=ClientSessionsResponse)
def get_my_sessions(
    client_id_cookie: str | None = Cookie(default=None, alias=CLIENT_ID_COOKIE_NAME),
):
    if not client_id_cookie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cookie client_id nao encontrado"
        )

    sessions = list_sessions_by_client(client_id_cookie)

    return ClientSessionsResponse(
        client_id=client_id_cookie,
        sessions=sessions
    )


@router.get("/{session_id}/history", response_model=SessionHistoryResponse)
def get_session_history(session_id: str):
    try:
        history = get_history_by_session(session_id)

        return SessionHistoryResponse(
            session_id=session_id,
            history=history
        )

    except ValueError:
        raise HTTPException(
            status_code=404,
            detail="Sessao nao encontrada"
        )


@router.get("/{session_id}/chat", response_model=SessionHistoryResponse)
def get_session_chat(session_id: str):
    try:
        history = get_history_by_session(session_id)

        return SessionHistoryResponse(
            session_id=session_id,
            history=history
        )

    except ValueError:
        raise HTTPException(
            status_code=404,
            detail="Sessao nao encontrada"
        )


@router.post("/{session_id}/messages", response_model=ChatResponse, status_code=status.HTTP_200_OK)
def send_session_message(session_id: str, request: ChatMessageRequest):
    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A mensagem nao pode estar vazia"
        )

    try:
        add_message_to_history(
            session_id=session_id,
            role="user",
            content=message
        )

        history = get_history_by_session(session_id)
        chatbot_response = generate_answer(message=message, history=history)

        add_message_to_history(
            session_id=session_id,
            role="assistant",
            content=chatbot_response
        )

        return ChatResponse(
            session_id=session_id,
            response=chatbot_response
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )
