from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 

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
