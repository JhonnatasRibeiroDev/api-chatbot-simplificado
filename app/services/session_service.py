from uuid import uuid4
#O uuid4 é uma biblioteca padrão do Python que serve para gerar IDs (identificadores

# Armazenamento em memória das sessões
# A chave será o session_id
# O valor será um dicionário com os dados daquela sessão
sessions={}

#funcao que cria uma sessao e retorna uma string 
def create_session() -> str:
    session_id = str(uuid4())

    sessions[session_id]= {
        "messages": []
    }

    return session_id

def session_exists(session_id: str) -> bool:
    return session_id in sessions

def add_message_to_history(session_id:str,role: str,content:str)-> None:
    if not session_exists(session_id):
        raise ValueError("Sessão não encontrada")
    
    sessions[session_id]["messages"].append({
           "role": role,
           "content": content
        } )

def get_history_by_session(session_id: str) -> list:
    if not session_exists(session_id):
        raise ValueError("Sessão não encontrada")

    return sessions[session_id]["messages"]






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
    


