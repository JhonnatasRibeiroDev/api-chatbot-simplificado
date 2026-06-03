from fastapi import APIRouter

from app.schemas.session_schema import SessionResponse
from app.services.session_service import create_session

'''
API ROUTER E SEPARAR ROTAS DA SESSAO PRINCIPAL 
app/routes/sessions.py  → rotas de sessões
app/routes/chat.py      → futuramente rotas de chat
app/main.py             → aplicação principal
'''

router = APIRouter (
    prefix="/api/sessions",
    tags=["Sessions"]

)


@router.post("",response_model=SessionResponse)
def create_new_session():
    session_id= create_session()

    return SessionResponse(session_id=session_id)
