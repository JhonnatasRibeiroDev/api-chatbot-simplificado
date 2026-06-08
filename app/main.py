from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from app.database import initialize_database
from app.routes.sessions import router as sessions_router
from app.routes.chat import router as chat_router

app = FastAPI(
    title="API Chatbot Simplificado",
    description="Backend do projeto Chatbot Multiusuário com LLM",
    version="0.1.0"
)

# Configuração de CORS
# Por enquanto, liberamos todas as origens para facilitar o desenvolvimento.
#CORS E TIPO UM MIDDLEARE QUE PERMITE ENVIAR REQUISICIOES DO FRONT PARA O BACKEND SEM BLOCKEIO
# Em produção, o ideal é trocar "*" pelo endereço real do frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    
)

#Registros as rotas de sessão na aplicação principal
app.include_router(sessions_router)
app.include_router(chat_router)


@app.on_event("startup")
def startup_event():
    initialize_database()

#NA pratica isso significa se alguem acessar /health responda OK API FUNCIONANDO 
#endpoint de teste
@app.get("/health")  #crio a rota da api
def health_check():
    return {
        "status":"ok",
        "message":"Api funcionando corretamente"
    }



