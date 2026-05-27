# Chatbot Multiusuário com LLM

Este projeto é um protótipo acadêmico desenvolvido para a disciplina de Tópicos em Computação Aplicada.

A aplicação permite que múltiplos usuários conversem simultaneamente com um chatbot baseado em LLM, mantendo o histórico de conversa isolado por sessão.

## Funcionalidades

- Criação de sessão com ID único
- Chat multiusuário
- Histórico isolado por sessão
- Integração com modelo LLM
- Endpoint público hospedado em AWS EC2
- Documentação de uso da API

## Tecnologias

- FastAPI
- Python
- LLM API
- Docker
- AWS EC2
- Next.js

## Endpoints

### Criar sessão

POST /api/sessions

### Enviar mensagem

POST /api/chat

### Consultar histórico

GET /api/sessions/{session_id}/history

### Health check

GET /health

## Como rodar localmente

```bash
docker compose up --build