# API Chatbot Simplificado

Backend academico em FastAPI para um chatbot multiusuario. No estado atual, o projeto possui a base da API, configuracao de CORS, endpoint de saude, criacao de sessoes, persistencia em SQLite, rota de chat, historico por sessao e integracao com LLM externo configuravel por variaveis de ambiente.

## Objetivo

O projeto tem como objetivo servir como uma API backend para um chatbot, separando responsabilidades em rotas, schemas, services e providers de LLM. Cada conversa usa um `session_id`, permitindo identificar conversas diferentes e manter o historico isolado por sessao.

## Tecnologias

- Python
- FastAPI
- Uvicorn
- Pydantic
- python-dotenv
- SQLite
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
- `app/database.py`: configura a conexao SQLite e cria as tabelas `sessions` e `messages`.
- `app/routes/sessions.py`: define as rotas de criacao de sessao, historico e listagem de conversas por cliente.
- `app/services/session_service.py`: gera o `session_id` com `uuid4`, persiste a sessao no SQLite e recupera historico por sessao.
- `app/repositories/sessions_repository.py`: executa operacoes SQL da tabela `sessions`.
- `app/repositories/messages_repository.py`: executa operacoes SQL da tabela `messages`.
- `app/services/message_service.py`: centraliza a gravacao e busca de mensagens no banco.
- `app/schemas/session_schema.py`: define os modelos de resposta de sessao, historico e listagem de sessoes por cliente.
- `app/routes/chat.py`: define a rota `POST /api/chat`, valida a sessao, salva a mensagem do usuario, chama o LLM e salva a resposta.
- `app/schemas/chat_schema.py`: define os modelos de entrada e saida da rota de chat.
- `app/services/llm_service.py`: monta o prompt com historico e mensagem atual, chama o provider configurado e registra metricas de tempo.
- `app/services/llm_providers/`: contem adaptadores para Gemini, OpenAI compativel e Ollama.
- `app/core/config.py`: le as configuracoes de LLM a partir do `.env`.

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

```env
LLM_PROVIDER=gemini
LLM_MODEL=gemini-3.5-flash
LLM_API_KEY=sua_chave_real
DATABASE_URL=sqlite:///./data/app.sqlite3
```

O arquivo `.env` contem segredo real e nao deve ser enviado para o Git.

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

### 4. Iniciar a API

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

| Metodo | Endpoint | Funcao |
| --- | --- | --- |
| `GET` | `/health` | Verifica se a API esta funcionando. |
| `POST` | `/api/sessions` | Cria uma nova sessao/conversa, salva no SQLite e grava/reutiliza o cookie `client_id`. |
| `GET` | `/api/sessions/me` | Lista as sessoes/conversas do usuario identificado pelo cookie `client_id`. |
| `GET` | `/api/sessions/clients/{client_id}` | Lista as sessoes/conversas de um cliente especifico. |
| `GET` | `/api/sessions/{session_id}/history` | Busca o historico de mensagens de uma sessao. |
| `GET` | `/api/sessions/{session_id}/chat` | Busca o chat completo de uma sessao. |
| `POST` | `/api/sessions/{session_id}/messages` | Envia mensagem para uma sessao e retorna a resposta da IA. |
| `POST` | `/api/chat` | Endpoint legado para enviar mensagem usando `session_id` no corpo da requisicao. |

### Exemplos rapidos

Criar sessao:

```http
POST /api/sessions
```

Body opcional:

```json
{
  "client_id": "user-123"
}
```

Enviar mensagem pelo endpoint novo:

```http
POST /api/sessions/{session_id}/messages
```

```json
{
  "message": "Ola, chatbot"
}
```

Buscar conversas pelo cookie:

```http
GET /api/sessions/me
```

Buscar conversas por `client_id`:

```http
GET /api/sessions/clients/user-123
```

Buscar mensagens/chat da sessao:

```http
GET /api/sessions/{session_id}/chat
```

## Como as sessoes funcionam

As sessoes sao persistidas no SQLite na tabela `sessions`. O dicionario `sessions`, definido em `app/services/session_service.py`, ainda e usado como apoio em memoria durante a execucao da API.

Exemplo conceitual:

```text
sessions
id | uuid_client | uuid_session | created_at
1  | user-123    | uuid-gerado  | 2026-06-07 13:03:36
```

Cada nova sessao recebe um UUID gerado por `uuid4`. Se o front nao enviar `client_id` e nao existir cookie `client_id`, o backend tambem gera um UUID para o cliente. A sessao e salva antes de o backend retornar `client_id` e `session_id` para o front.

O backend tambem grava o `client_id` em cookie HTTP-only. Com isso, o endpoint `GET /api/sessions/me` consegue recuperar as conversas antigas do mesmo visitante sem exigir que o front envie o `client_id` manualmente.

As mensagens do chat sao persistidas na tabela `messages`:

```text
messages
id | uuid_client | uuid_session | role      | mensagem
1  | user-123    | uuid-gerado  | user      | Ola
2  | user-123    | uuid-gerado  | assistant | Ola, tudo bem?
```

O historico da sessao e recuperado buscando as mensagens pelo `uuid_session`.

## Estado atual do projeto

Implementado:

- Aplicacao FastAPI.
- Middleware de CORS liberando todas as origens.
- Endpoint `GET /health`.
- Endpoint `POST /api/sessions`.
- Endpoint `GET /api/sessions/me`.
- Endpoint `GET /api/sessions/clients/{client_id}`.
- Endpoint `GET /api/sessions/{session_id}/history`.
- Endpoint `GET /api/sessions/{session_id}/chat`.
- Endpoint `POST /api/sessions/{session_id}/messages`.
- Schema de resposta para sessao.
- Persistencia de sessoes no SQLite.
- Persistencia de mensagens no SQLite.
- Recuperacao de historico pelo SQLite.
- Listagem de conversas por cliente.
- Endpoint `POST /api/chat`.
- Integracao do chat com servico LLM.
- Configuracoes de LLM via variaveis de ambiente.
- Providers para Gemini, OpenAI, OpenAI compativel e Ollama.
- Logs de performance da chamada ao LLM.
- Testes unitarios para servico LLM, rota de chat e concorrencia.
- Testes reais de tempo com requisicoes sequenciais e simultaneas.
- Tratamento amigavel para falhas da API do LLM.

Ainda nao implementado:

- Pipeline RAG.
- Dockerfile e Docker Compose funcionais.

## Observacoes importantes

- O CORS esta configurado com `allow_origins=["*"]`, adequado para desenvolvimento, mas deve ser restringido em producao.
- O SQLite usa o arquivo definido em `DATABASE_URL`, por padrao `data/app.sqlite3`.
- O `uuid_client` e recebido pelo `POST /api/sessions`, reaproveitado do cookie `client_id` ou gerado automaticamente quando nao existir.
- `Dockerfile` e `docker-compose.yml` ainda nao estao funcionais.
- `.env.example` documenta as variaveis esperadas, mas a chave real deve ficar apenas no `.env` local.
- A pasta `.venv` e arquivos de cache Python devem permanecer fora do versionamento, conforme `.gitignore`.

## Comando rapido

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
