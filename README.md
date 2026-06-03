# API Chatbot Simplificado

Backend academico em FastAPI para um chatbot multiusuario. No estado atual, o projeto ja possui a base da API, configuracao de CORS, endpoint de saude e criacao de sessoes em memoria. As partes de chat, LLM e RAG existem como arquivos de preparacao, mas ainda nao possuem implementacao.

## Objetivo

O projeto tem como objetivo servir como uma API backend para um chatbot, separando responsabilidades em rotas, schemas e services. A primeira funcionalidade implementada e a criacao de sessoes, permitindo identificar conversas diferentes por meio de um `session_id`.

## Tecnologias

- Python
- FastAPI
- Uvicorn
- Pydantic
- python-dotenv

As dependencias do projeto estao listadas em `requirements.txt`.

## Estrutura do projeto

```text
.
├── app/
│   ├── main.py
│   ├── core/
│   │   └── config.py
│   ├── routes/
│   │   ├── chat.py
│   │   └── sessions.py
│   ├── schemas/
│   │   ├── chat_schema.py
│   │   └── session_schema.py
│   └── services/
│       ├── llm_service.py
│       └── session_service.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## Responsabilidades dos arquivos

- `app/main.py`: cria a aplicacao FastAPI, configura CORS, registra as rotas de sessoes e expoe o endpoint `/health`.
- `app/routes/sessions.py`: define a rota `POST /api/sessions` para criar uma nova sessao.
- `app/services/session_service.py`: gera o `session_id` com `uuid4` e armazena a sessao em memoria.
- `app/schemas/session_schema.py`: define o modelo de resposta da criacao de sessao.
- `app/routes/chat.py`: arquivo reservado para futuras rotas de chat.
- `app/schemas/chat_schema.py`: arquivo reservado para futuros schemas de chat.
- `app/services/llm_service.py`: arquivo reservado para futura integracao com LLM.
- `app/core/config.py`: arquivo reservado para futuras configuracoes da aplicacao.

## Como executar localmente

### 1. Criar e ativar ambiente virtual

No Windows:
Recomendase ter o wsl/unbutu instalado
```powershell
wsl 
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

No Linux, macOS ou WSL:

```bash
python -m venv .venv  #instalar o ambiente virtual 
source .venv/bin/activate #iniciar o ambiente virtual
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt  #dependecias dos projeto
```

### 3. Iniciar a API

```bash
uvicorn app.main:app --reload
```

Por padrao, a API ficara disponivel em:

```text
http://127.0.0.1:8000
```

## Documentacao interativa

Com a API em execucao, acesse:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Endpoints disponiveis

### Health check

Verifica se a API esta respondendo.

```http
GET /health
```

Resposta esperada:

```json
{
  "status": "ok",
  "message": "Api funcionando corretamente"
}
```

### Criar sessao

Cria uma nova sessao de conversa e retorna um identificador unico.

```http
POST /api/sessions
```

Resposta esperada:

```json
{
  "session_id": "uuid-gerado"
}
```

Exemplo com `curl`:

```bash
curl -X POST http://127.0.0.1:8000/api/sessions
```

## Como as sessoes funcionam

As sessoes sao armazenadas em memoria no dicionario `sessions`, definido em `app/services/session_service.py`.

Exemplo conceitual:

```python
sessions = {
    "session-id": {
        "messages": []
    }
}
```

Cada nova sessao recebe um UUID gerado por `uuid4`. Como o armazenamento e em memoria, os dados sao perdidos quando o servidor e reiniciado.

## Estado atual do projeto

Implementado:

- Aplicacao FastAPI.
- Middleware de CORS liberando todas as origens.
- Endpoint `GET /health`.
- Endpoint `POST /api/sessions`.
- Schema de resposta para sessao.
- Service de criacao de sessao em memoria.

Ainda nao implementado:

- Rotas de chat.
- Schemas de requisicao e resposta para mensagens.
- Integracao com LLM.
- Pipeline RAG.
- Persistencia em banco de dados.
- Configuracoes via `.env`.
- Dockerfile e Docker Compose funcionais.
- Testes automatizados.

## Observacoes importantes

- O CORS esta configurado com `allow_origins=["*"]`, adequado para desenvolvimento, mas deve ser restringido em producao.
- O armazenamento atual das sessoes nao e persistente.
- `Dockerfile`, `docker-compose.yml` e `.env.example` existem, mas ainda estao vazios.
- A pasta `.venv` e arquivos de cache Python devem permanecer fora do versionamento, conforme `.gitignore`.

## Comando rapido

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
