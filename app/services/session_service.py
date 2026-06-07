from uuid import uuid4

from app.repositories.sessions_repository import (
    create_session_record,
    get_client_by_session,
    get_sessions_by_client,
    session_record_exists,
)
from app.services.message_service import DEFAULT_UUID_CLIENT, get_session_messages, save_message
#O uuid4 é uma biblioteca padrão do Python que serve para gerar IDs (identificadores

# Armazenamento em memória das sessões
# A chave será o session_id
# O valor será um dicionário com os dados daquela sessão
sessions={}

#funcao que cria uma sessao e retorna os identificadores
def create_session(client_id: str | None = None) -> dict:
    uuid_client = client_id or str(uuid4())
    session_id = str(uuid4())

    sessions[session_id]= {
        "client_id": uuid_client,
        "messages": []
    }

    create_session_record(
        uuid_client=uuid_client,
        uuid_session=session_id
    )

    return {
        "client_id": uuid_client,
        "session_id": session_id
    }

def session_exists(session_id: str) -> bool:
    return session_id in sessions or session_record_exists(session_id)

def ensure_session_in_memory(session_id: str) -> None:
    if session_id not in sessions:
        sessions[session_id] = {
            "client_id": get_client_by_session(session_id) or DEFAULT_UUID_CLIENT,
            "messages": []
        }

def get_client_id_by_session(session_id: str) -> str:
    ensure_session_in_memory(session_id)
    return sessions[session_id].get("client_id") or DEFAULT_UUID_CLIENT

def add_message_to_history(session_id:str,role: str,content:str)-> None:
    if not session_exists(session_id):
        raise ValueError("Sessão não encontrada")
    
    ensure_session_in_memory(session_id)

    sessions[session_id]["messages"].append({
           "role": role,
           "content": content
        } )

    save_message(
        uuid_client=get_client_id_by_session(session_id),
        uuid_session=session_id,
        role=role,
        content=content
    )

def get_history_by_session(session_id: str) -> list:
    if not session_exists(session_id):
        raise ValueError("Sessão não encontrada")

    ensure_session_in_memory(session_id)

    messages = get_session_messages(session_id)

    if messages:
        return messages

    return sessions[session_id]["messages"]


def list_sessions_by_client(client_id: str) -> list[dict]:
    return get_sessions_by_client(client_id)






'''
O ID identifica um acesso, não uma pessoa.
sessions = {
    "abc-123-xyz": {
        "messages": ["Olá!", "Como posso ajudar?", "Quero cancelar meu plano."]
    },
    "def-456-uuu": {
        "messages": ["Qual a previsão do tempo?"]
    },
    "ghi-789-lll": {
        "messages": []  # Esse acabou de entrar, a lista está vazia!
    }
}

'''
    


