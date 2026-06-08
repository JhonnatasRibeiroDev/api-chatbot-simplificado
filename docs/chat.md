# Feature: Chat — Envio de Mensagens e Geração de Resposta

## O que é

A feature de chat recebe a mensagem do usuário, persiste no banco, consulta o histórico da sessão, envia tudo ao LLM configurado e retorna a resposta gerada. Todo o contexto da conversa é preservado entre turnos.

---

## Arquivos envolvidos

| Camada | Arquivo |
|---|---|
| Rota (HTTP) | `app/routes/chat.py`, `app/routes/sessions.py` |
| Serviço LLM | `app/services/llm_service.py` |
| Serviço de sessão | `app/services/session_service.py` |
| Serviço de mensagem | `app/services/message_service.py` |
| Repositório | `app/repositories/messages_repository.py` |
| Schemas | `app/schemas/chat_schema.py` |

---

## Endpoints

### `POST /api/sessions/{session_id}/messages` — Enviar mensagem (endpoint atual)

**Body:**
```json
{ "message": "Qual a capital do Brasil?" }
```

**Resposta `200`:**
```json
{
  "session_id": "abc...",
  "response": "A capital do Brasil é Brasília."
}
```

**Erros:**
- `400` — mensagem vazia
- `404` — `session_id` não encontrado

---

### `POST /api/chat` — Enviar mensagem (endpoint legado)

Mesmo comportamento, mas recebe o `session_id` no corpo da requisição.

**Body:**
```json
{
  "session_id": "abc...",
  "message": "Qual a capital do Brasil?"
}
```

---

## Fluxo interno

```
POST /api/sessions/{session_id}/messages
  └─ routes/sessions.py: send_session_message()
       ├─ Valida: mensagem não pode ser vazia
       ├─ session_service.add_message_to_history(session_id, "user", message)
       │    └─ message_service.save_message()
       │         └─ messages_repository.create_message() → INSERT INTO messages
       ├─ session_service.get_history_by_session(session_id)
       │    └─ messages_repository.get_messages_by_session() → SELECT FROM messages
       ├─ llm_service.generate_answer(message, history)
       │    ├─ Monta prompt com histórico formatado
       │    └─ provider.generate(prompt) → resposta do LLM
       └─ session_service.add_message_to_history(session_id, "assistant", response)
            └─ messages_repository.create_message() → INSERT INTO messages
```

---

## Construção do prompt (`llm_service.py`)

O prompt enviado ao LLM segue este formato:

```
Voce e um assistente virtual util, claro e objetivo.
Use o historico da conversa para manter contexto quando for relevante.

Historico da conversa:
user: <mensagem anterior>
assistant: <resposta anterior>
...

Mensagem atual do usuario:
<mensagem atual>
```

O histórico completo da sessão é incluído em cada chamada — não há janela deslizante implementada.

---

## Tratamento de erros do LLM

Se o provedor LLM lançar qualquer exceção, `generate_answer` captura o erro, registra no log com métricas de tempo e retorna a mensagem amigável:

> "Nao consegui gerar uma resposta agora. Tente novamente em instantes."

---

## Schemas Pydantic

| Modelo | Uso |
|---|---|
| `ChatRequest` | Body do `POST /api/chat` (legado) |
| `ChatMessageRequest` | Body do `POST /api/sessions/{id}/messages` |
| `ChatResponse` | Resposta de ambos os endpoints |

---

## Logging de performance

`llm_service.generate_answer` registra em log os tempos de cada etapa:

| Campo | Significado |
|---|---|
| `provider_s` | Tempo para instanciar o provider |
| `prompt_s` | Tempo para montar o prompt |
| `generate_s` | Tempo de resposta do LLM |
| `total_s` | Tempo total da função |
| `prompt_chars` | Tamanho do prompt em caracteres |
| `answer_chars` | Tamanho da resposta em caracteres |
