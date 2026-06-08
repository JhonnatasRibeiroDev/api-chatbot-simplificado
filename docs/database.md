# Feature: Banco de Dados (SQLite)

## O que é

A aplicação usa SQLite como banco de dados persistente para armazenar sessões e mensagens. A inicialização é idempotente (segura para chamadas repetidas), thread-safe e acontece automaticamente no startup da aplicação.

---

## Arquivo principal

`app/database.py`

---

## Schema

### Tabela `sessions`

Registra cada sessão criada, associando um cliente a uma conversa.

```sql
CREATE TABLE IF NOT EXISTS sessions (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid_client  TEXT NOT NULL,
    uuid_session TEXT NOT NULL UNIQUE,
    created_at   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

| Coluna | Descrição |
|---|---|
| `id` | Chave primária autoincremental |
| `uuid_client` | Identificador do cliente (persistido como cookie no frontend) |
| `uuid_session` | Identificador único da sessão (gerado com `uuid4`) |
| `created_at` | Data/hora de criação (UTC, formato ISO 8601) |

---

### Tabela `messages`

Armazena cada mensagem trocada em uma sessão.

```sql
CREATE TABLE IF NOT EXISTS messages (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid_client  TEXT NOT NULL,
    uuid_session TEXT NOT NULL,
    role         TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    mensagem     TEXT NOT NULL
);
```

| Coluna | Descrição |
|---|---|
| `id` | Chave primária autoincremental; define a ordem cronológica das mensagens |
| `uuid_client` | Identificador do cliente dono da mensagem |
| `uuid_session` | Sessão à qual a mensagem pertence |
| `role` | Quem enviou: `user`, `assistant` ou `system` |
| `mensagem` | Conteúdo textual da mensagem |

---

## Inicialização

A função `initialize_database()` é chamada no evento `startup` do FastAPI (`app/main.py`):

```python
@app.on_event("startup")
def startup_event():
    initialize_database()
```

A função é protegida por um `threading.Lock` e uma flag `_DATABASE_INITIALIZED` para garantir que o schema seja criado exatamente uma vez, mesmo em ambientes com múltiplas threads.

---

## Conexão

`get_connection()` abre uma conexão SQLite configurada com:

| Pragma / Opção | Valor | Motivo |
|---|---|---|
| `check_same_thread` | `False` | Permite uso da conexão em múltiplas threads (FastAPI) |
| `timeout` | `30s` | Aguarda liberação do banco antes de falhar |
| `busy_timeout` | `30000ms` | Aguarda lock em nível de statement SQL |
| `foreign_keys` | `ON` | Garante integridade referencial |
| `row_factory` | `sqlite3.Row` | Retorna linhas como dicionários acessíveis por nome de coluna |

---

## Localização do arquivo de banco

Controlada pela variável de ambiente `DATABASE_URL` (padrão: `sqlite:///./data/app.sqlite3`).

O diretório `data/` é criado automaticamente se não existir. O caminho relativo é resolvido a partir da raiz do projeto.

---

## Acesso thread-safe a escrita

Operações de escrita (`INSERT`) em `sessions_repository.py` e `messages_repository.py` usam o `DATABASE_LOCK` global para serializar escritas concorrentes e evitar corrupção de dados.
