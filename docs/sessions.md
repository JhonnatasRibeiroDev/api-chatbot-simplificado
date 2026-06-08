# Feature: Gerenciamento de Sessões

## O que é

A feature de sessões controla a identidade do usuário e o ciclo de vida de cada conversa. Cada cliente é identificado por um `client_id` (UUID persistido via cookie HTTP-only no navegador), e cada conversa individual recebe um `session_id` (UUID único). Um cliente pode ter múltiplas sessões ao longo do tempo.

---

## Arquivos envolvidos

| Camada | Arquivo |
|---|---|
| Rota (HTTP) | `app/routes/sessions.py` |
| Serviço (lógica) | `app/services/session_service.py` |
| Repositório (banco) | `app/repositories/sessions_repository.py` |
| Schemas (contratos) | `app/schemas/session_schema.py` |

---

## Endpoints

### `POST /api/sessions` — Criar nova sessão

Cria uma nova sessão para o cliente. Se o cookie `client_id` já existir, a nova sessão é associada ao mesmo cliente. Caso contrário, um novo `client_id` é gerado.

**Cookie lido:** `client_id` (httponly, enviado automaticamente pelo navegador)

**Body (opcional):**
```json
{ "client_id": "uuid-opcional" }
```

**Resposta `200`:**
```json
{
  "client_id": "550e8400-e29b-41d4-a716-446655440000",
  "session_id": "3f7e4567-e89b-12d3-a456-426614174000"
}
```

**Efeito colateral:** define o cookie `client_id` na resposta (httponly, SameSite=lax, validade de 1 ano).

---

### `GET /api/sessions/me` — Listar sessões do cliente autenticado

Retorna todas as sessões do cliente identificado pelo cookie `client_id`.

**Cookie necessário:** `client_id`

**Resposta `200`:**
```json
{
  "client_id": "550e8400-...",
  "sessions": [
    { "session_id": "abc...", "created_at": "2024-01-15T10:00:00" }
  ]
}
```

**Erro `404`:** cookie `client_id` ausente.

---

### `GET /api/sessions/clients/{client_id}` — Listar sessões por client_id

Mesmo resultado de `/me`, mas recebe o `client_id` diretamente na URL. Útil para consultas administrativas ou debugging.

---

### `GET /api/sessions/{session_id}/history` — Histórico de uma sessão

Retorna todas as mensagens da sessão em ordem cronológica.

**Resposta `200`:**
```json
{
  "session_id": "abc...",
  "history": [
    { "role": "user", "content": "Olá!" },
    { "role": "assistant", "content": "Olá! Como posso ajudar?" }
  ]
}
```

**Erro `404`:** sessão não encontrada.

---

### `GET /api/sessions/{session_id}/chat`

Alias de `/history`. Retorna o mesmo conteúdo.

---

## Fluxo interno

```
POST /api/sessions
  └─ routes/sessions.py: create_new_session()
       └─ services/session_service.py: create_session(client_id)
            ├─ Gera uuid_client (ou reutiliza o recebido)
            ├─ Gera uuid_session
            ├─ Registra em memória: sessions[session_id] = {...}
            └─ repositories/sessions_repository.py: create_session_record()
                 └─ INSERT INTO sessions (uuid_client, uuid_session)
```

**Armazenamento duplo:** a sessão é mantida em um dicionário Python em memória (`sessions = {}` em `session_service.py`) E persistida no SQLite. Ao reiniciar o servidor, a sessão é recuperada do banco quando necessária (`ensure_session_in_memory`).

---

## Schemas Pydantic

| Modelo | Uso |
|---|---|
| `SessionRequest` | Body opcional do `POST /api/sessions` |
| `SessionResponse` | Resposta do `POST /api/sessions` |
| `SessionHistoryResponse` | Resposta dos endpoints de histórico |
| `ClientSessionsResponse` | Resposta dos endpoints de listagem |
| `ClientSessionResponse` | Item da lista de sessões |
| `MessageResponse` | Item do histórico (`role` + `content`) |
