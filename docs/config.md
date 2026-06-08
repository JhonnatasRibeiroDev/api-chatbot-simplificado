# Feature: Configuração via Variáveis de Ambiente

## O que é

Toda a configuração da aplicação é feita por variáveis de ambiente, carregadas automaticamente de um arquivo `.env` na raiz do projeto (usando `python-dotenv`). Não há valores hardcoded no código além dos defaults declarados explicitamente.

---

## Arquivos envolvidos

| Arquivo | Responsabilidade |
|---|---|
| `app/core/config.py` | Define `LLMConfig` e a função `get_llm_config()` |
| `.env.example` | Modelo de arquivo `.env` com todas as variáveis disponíveis |
| `app/database.py` | Lê `DATABASE_URL` diretamente com `os.getenv` |

---

## Variáveis de ambiente

### Configuração do LLM

| Variável | Padrão | Descrição |
|---|---|---|
| `LLM_PROVIDER` | `gemini` | Provedor LLM a usar. Valores aceitos: `gemini`, `openai`, `openai_compatible`, `ollama` |
| `LLM_MODEL` | `gemini-3.5-flash` | Nome/ID do modelo a usar no provedor configurado |
| `LLM_API_KEY` | `""` (vazio) | Chave de API. Obrigatória para `gemini` e `openai` |
| `LLM_BASE_URL` | `""` (vazio) | URL base da API. Obrigatória para `openai_compatible`. Opcional para `ollama` |

### Configuração do banco de dados

| Variável | Padrão | Descrição |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./data/app.sqlite3` | Caminho do banco SQLite no formato `sqlite:///caminho` |

---

## Como funciona

`get_llm_config()` é chamada a cada requisição em `llm_service.generate_answer`, garantindo que mudanças no `.env` sejam lidas sem precisar reiniciar o servidor (desde que `load_dotenv()` seja chamado antes).

```python
@dataclass(frozen=True)
class LLMConfig:
    provider: str
    model: str
    api_key: str
    base_url: str

def get_llm_config() -> LLMConfig:
    return LLMConfig(
        provider=os.getenv("LLM_PROVIDER", "gemini"),
        model=os.getenv("LLM_MODEL", "gemini-3.5-flash"),
        api_key=os.getenv("LLM_API_KEY", ""),
        base_url=os.getenv("LLM_BASE_URL", ""),
    )
```

`LLMConfig` é um `dataclass(frozen=True)` — imutável após criação, seguro para passar entre camadas sem risco de modificação acidental.

---

## Setup inicial

1. Copiar `.env.example` para `.env`:
   ```bash
   cp .env.example .env
   ```

2. Preencher as variáveis obrigatórias para o provedor escolhido. Exemplo para Gemini:
   ```env
   LLM_PROVIDER=gemini
   LLM_MODEL=gemini-1.5-flash
   LLM_API_KEY=sua-chave-aqui
   ```

3. Iniciar a aplicação. O `.env` é carregado automaticamente pelo `load_dotenv()` em `config.py` e `database.py`.

---

## Notas

- Em produção (Docker), as variáveis devem ser definidas no ambiente do container, não em um arquivo `.env`.
- O arquivo `.env` nunca deve ser commitado. Ele já está no `.gitignore`.
- Para detalhes sobre qual modelo escolher por provedor, consulte `docs/llm_model_choice.md`.
