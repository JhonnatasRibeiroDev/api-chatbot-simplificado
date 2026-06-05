# API Chatbot Simplificado

Backend academico em FastAPI para um chatbot multiusuario. No estado atual, o projeto possui a base da API, configuracao de CORS, endpoint de saude, criacao de sessoes em memoria, rota de chat, historico por sessao e integracao com LLM externo configuravel por variaveis de ambiente.

## Objetivo

O projeto tem como objetivo servir como uma API backend para um chatbot, separando responsabilidades em rotas, schemas, services e providers de LLM. Cada conversa usa um `session_id`, permitindo identificar conversas diferentes e manter o historico isolado por sessao.

## Tecnologias

- Python
- FastAPI
- Uvicorn
- Pydantic
- python-dotenv
- Google GenAI SDK
- httpx

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
- `app/routes/chat.py`: define a rota `POST /api/chat`, valida a sessao, salva a mensagem do usuario, chama o LLM e salva a resposta.
- `app/schemas/chat_schema.py`: define os modelos de entrada e saida da rota de chat.
- `app/services/llm_service.py`: monta o prompt com historico e mensagem atual, chama o provider configurado e registra metricas de tempo.
- `app/services/llm_providers/`: contem adaptadores para Gemini, OpenAI compativel e Ollama.
- `app/core/config.py`: le as configuracoes de LLM a partir do `.env`.
- `Dockerfile`: define a imagem Docker do backend, instala as dependencias e inicia a API com Uvicorn.
- `docker-compose.yml`: sobe o backend em container e publica a porta `8000`.
- `.dockerignore`: remove arquivos locais, cache, ambiente virtual e segredos do contexto de build.

## Como executar localmente

### 1. Criar e ativar ambiente virtual

No Windows:
Recomendase ter o wsl/unbutu instalado
```powershell
wsl 
python3 -m venv .venv
source .venv/bin/activate
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

### 3. Configurar variaveis de ambiente

Crie um arquivo `.env` local com base no `.env.example`:

No Linux, macOS ou WSL:

```bash
cp .env.example .env
```

No Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Depois edite o arquivo `.env` com as credenciais reais:

```env
LLM_PROVIDER=gemini
LLM_MODEL=gemini-3.5-flash
LLM_API_KEY=sua_chave_real
LLM_BASE_URL=
```

O arquivo `.env` contem segredo real e nao deve ser enviado para o Git.

### 4. Iniciar a API com Uvicorn

```bash
uvicorn app.main:app --reload
```

Por padrao, a API ficara disponivel em:

```text
http://127.0.0.1:8000
```

### 5. Testar o endpoint de saude

```bash
curl http://127.0.0.1:8000/health
```

Resposta esperada:

```json
{"status":"ok","message":"Api funcionando corretamente"}
```

## Como executar com Docker

Antes de iniciar, mantenha o Docker Desktop aberto e crie o arquivo `.env` com base no `.env.example`. Nao e necessario criar ambiente virtual nem instalar dependencias localmente quando a execucao for feita com Docker.

### 1. Construir a imagem

```bash
docker compose build
```

### 2. Iniciar o backend

```bash
docker compose up -d
```

A API ficara disponivel em:

```text
http://localhost:8000
```

### 3. Testar se a aplicacao subiu

```bash
curl http://localhost:8000/health
```

Resposta esperada:

```json
{"status":"ok","message":"Api funcionando corretamente"}
```

### 4. Verificar ou parar o container

```bash
docker compose ps
docker compose down
```

## Como mudar o modelo LLM

### Atualizacao do estado atual

O modelo ativo e definido no arquivo `.env`. Para trocar apenas o modelo dentro do mesmo provider, altere `LLM_MODEL` e reinicie a API.

Exemplo com Gemini:

```env
LLM_PROVIDER=gemini
LLM_MODEL=gemini-3.5-flash
LLM_API_KEY=sua_chave_real
```

Exemplo trocando apenas o modelo Gemini:

```env
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.5-pro
LLM_API_KEY=sua_chave_real
```
Outros modelos para testar:
gemma-4-31b-it
gemma-4-26b-a4b-it


Reiniciar a API significa parar o servidor com `Ctrl + C` e iniciar de novo:

```bash
uvicorn app.main:app --reload
```

Isso e necessario porque o `.env` e carregado quando a aplicacao sobe.

Providers suportados no codigo atual:

- `gemini`: usa Google GenAI SDK e exige `LLM_API_KEY`.
- `openai`: usa endpoint compativel com OpenAI em `https://api.openai.com/v1` e exige `LLM_API_KEY`.
- `openai_compatible`: usa `LLM_BASE_URL`, util para servidores compativeis com OpenAI.
- `ollama`: usa `LLM_BASE_URL` ou `http://localhost:11434`.

Exemplo com Ollama local:

```env
LLM_PROVIDER=ollama
LLM_MODEL=llama3.1
LLM_API_KEY=
LLM_BASE_URL=http://localhost:11434
```

O backend usa uma camada de providers para comunicacao com modelos de linguagem. A rota de chat chama apenas o servico de LLM, e o provider ativo traduz essa chamada para Gemini, OpenAI compativel ou Ollama.

  > O backend usa uma camada de abstração para comunicação com modelos de linguagem. A rota de chat chama apenas o serviço de LLM, sem
  > depender diretamente de Gemini, OpenAI, Ollama ou qualquer outro fornecedor. A escolha do modelo ativo é feita por variáveis de ambiente,
  > como LLM_PROVIDER, LLM_MODEL, LLM_API_KEY e LLM_BASE_URL. Cada fornecedor possui um adaptador próprio, responsável por traduzir a chamada
  > genérica do sistema para a API específica daquele modelo. Com isso, a estrutura principal do backend permanece igual, e a troca de modelo
  > acontece apenas pela configuração.

## Documentacao interativa

Com a API em execucao, acesse:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Endpoints disponiveis

### Health check

Verifica se a API esta respondendo.

- Metodo: `GET`
- Rota: `/health`
- Objetivo: confirmar que o backend esta online.
- Corpo da requisicao: nao possui.

```http
GET /health
```

Exemplo com `curl`:

```bash
curl http://127.0.0.1:8000/health
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

- Metodo: `POST`
- Rota: `/api/sessions`
- Objetivo: criar uma sessao para iniciar uma conversa.
- Corpo da requisicao: nao possui.

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

### Enviar mensagem ao chat

Envia uma mensagem para uma sessao existente. O backend salva a mensagem do usuario, envia a mensagem e o historico da sessao ao LLM configurado e salva a resposta do assistente.

- Metodo: `POST`
- Rota: `/api/chat`
- Objetivo: enviar uma mensagem do usuario e receber a resposta do chatbot.
- Corpo da requisicao: JSON com `session_id` e `message`.

```http
POST /api/chat
```

Payload:

```json
{
  "session_id": "uuid-gerado",
  "message": "Ola, chatbot"
}
```

Exemplo com `curl`:

```bash
curl -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id":"uuid-gerado","message":"Ola, chatbot"}'
```

Resposta esperada:

```json
{
  "session_id": "uuid-gerado",
  "response": "resposta gerada pelo modelo"
}
```

Se a API do LLM falhar ou a chave nao estiver configurada, a resposta sera:

```text
Não consegui gerar uma resposta agora. Tente novamente em instantes.
```

### Consultar historico da sessao

Retorna todas as mensagens registradas em uma sessao.

- Metodo: `GET`
- Rota: `/api/sessions/{session_id}/history`
- Objetivo: consultar o historico de mensagens da sessao.
- Corpo da requisicao: nao possui.
- Parametro de rota: `session_id`, identificador retornado em `POST /api/sessions`.

```http
GET /api/sessions/{session_id}/history
```

Exemplo com `curl`:

```bash
curl http://127.0.0.1:8000/api/sessions/uuid-gerado/history
```

Resposta esperada:

```json
{
  "session_id": "uuid-gerado",
  "history": [
    {
      "role": "user",
      "content": "Ola, chatbot"
    },
    {
      "role": "assistant",
      "content": "Ola! Como posso ajudar voce hoje?"
    }
  ]
}
```

Se a sessao nao existir, a API retorna:

```json
{
  "detail": "Sessao nao encontrada"
}
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
- Endpoint `POST /api/chat`.
- Integracao do chat com servico LLM.
- Configuracoes de LLM via variaveis de ambiente.
- Providers para Gemini, OpenAI, OpenAI compativel e Ollama.
- Logs de performance da chamada ao LLM.
- Testes unitarios para servico LLM, rota de chat e concorrencia.
- Testes reais de tempo com requisicoes sequenciais e simultaneas.
- Tratamento amigavel para falhas da API do LLM.
- Dockerfile e Docker Compose funcionais para execucao local em container.

Ainda nao implementado:

- Pipeline RAG.
- Persistencia em banco de dados.

## Observacoes importantes

- O CORS esta configurado com `allow_origins=["*"]`, adequado para desenvolvimento, mas deve ser restringido em producao.
- O armazenamento atual das sessoes nao e persistente.
- `.env.example` documenta as variaveis esperadas, mas a chave real deve ficar apenas no `.env` local.
- A pasta `.venv` e arquivos de cache Python devem permanecer fora do versionamento, conforme `.gitignore`.

## Comando rapido

Sem Docker:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Com Docker:

```bash
docker compose up -d
```
