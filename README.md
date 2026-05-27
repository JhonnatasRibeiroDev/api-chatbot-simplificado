# Backend — Chatbot Multiusuário com LLM

Backend do projeto **Chatbot Multiusuário com LLM**, desenvolvido para permitir que múltiplos usuários interajam simultaneamente com um chatbot, mantendo o histórico de conversa isolado por sessão.

O sistema gera um `session_id` único para cada usuário conectado, utiliza esse identificador para controlar o histórico individual da conversa e envia as mensagens para um modelo LLM responsável por gerar as respostas.

---

## Objetivo do Backend

O backend tem como objetivo fornecer uma API capaz de:

- Criar sessões únicas para usuários diferentes;
- Manter o histórico de conversa separado por sessão;
- Receber perguntas dos usuários;
- Enviar o contexto da conversa para um modelo LLM;
- Retornar respostas geradas pelo chatbot;
- Disponibilizar endpoints públicos para uso pelo frontend ou por ferramentas como `curl`, Postman e Insomnia.

---

## Tecnologias Utilizadas

- Python
- FastAPI
- Uvicorn
- UUID
- API de LLM, como Gemini, OpenAI ou outra escolhida pelo grupo
- Docker
- Docker Compose

---

## Estrutura Sugerida do Backend

```txt
backend/
├── app/
│   ├── main.py
│   ├── routes/
│   │   ├── chat.py
│   │   └── sessions.py
│   ├── services/
│   │   ├── llm_service.py
│   │   └── session_service.py
│   ├── schemas/
│   │   ├── chat_schema.py
│   │   └── session_schema.py
│   └── core/
│       └── config.py
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md
