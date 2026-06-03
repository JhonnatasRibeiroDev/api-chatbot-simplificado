from fastapi import APIRouter,HTTPException

from app.schemas.session_schema import SessionResponse
from app.services.session_service import create_session

'''
API ROUTER E SEPARAR ROTAS DA SESSAO PRINCIPAL 
app/routes/sessions.py  → rotas de sessões
app/routes/chat.py      → futuramente rotas de chat
app/main.py             → aplicação principal
'''
from app.schemas.session_schema import (
    SessionResponse,
    SessionHistoryResponse,
)
from app.services.session_service import (
    create_session,
    get_history_by_session,
)


router = APIRouter (
    prefix="/api/sessions",
    tags=["Sessions"]

)


@router.post("",response_model=SessionResponse)
def create_new_session():
    session_id= create_session()

    return SessionResponse(session_id=session_id)


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
            detail="Sessão não encontrada"
        )