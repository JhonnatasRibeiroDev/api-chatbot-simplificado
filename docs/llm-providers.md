# Feature: Provedores LLM (Arquitetura Plugável)

## O que é

O sistema de provedores LLM permite trocar o modelo de linguagem utilizado pelo chatbot apenas alterando variáveis de ambiente, sem modificar o código. A arquitetura usa um padrão Factory + classe base abstrata para garantir que qualquer provedor novo siga o mesmo contrato.

---

## Arquivos envolvidos

| Arquivo | Responsabilidade |
|---|---|
| `app/services/llm_providers/base.py` | Interface abstrata `LLMProvider` |
| `app/services/llm_providers/factory.py` | Factory: instancia o provider correto com base na config |
| `app/services/llm_providers/gemini_provider.py` | Implementação Google Gemini |
| `app/services/llm_providers/openai_compatible_provider.py` | Implementação OpenAI e APIs compatíveis |
| `app/services/llm_providers/ollama_provider.py` | Implementação Ollama (modelos locais) |
| `app/core/config.py` | Lê as variáveis de ambiente e retorna `LLMConfig` |

---

## Provedores suportados

| `LLM_PROVIDER` | Provedor | Requer `LLM_API_KEY` | Requer `LLM_BASE_URL` |
|---|---|---|---|
| `gemini` | Google Gemini | Sim | Não |
| `openai` | OpenAI | Sim | Não (usa `https://api.openai.com/v1`) |
| `openai_compatible` | Qualquer API no padrão OpenAI | Não | Sim |
| `ollama` | Ollama local | Não | Não (usa `http://localhost:11434`) |

---

## Como funciona a Factory

```python
# app/services/llm_providers/factory.py
def create_llm_provider(config: LLMConfig) -> LLMProvider:
    provider = config.provider.lower().strip()

    if provider == "gemini":
        return GeminiProvider(api_key=config.api_key, model=config.model)

    if provider == "openai":
        return OpenAICompatibleProvider(
            api_key=config.api_key,
            model=config.model,
            base_url=config.base_url or DEFAULT_OPENAI_BASE_URL,
        )

    if provider == "openai_compatible":
        return OpenAICompatibleProvider(
            api_key=config.api_key,
            model=config.model,
            base_url=config.base_url,
        )

    if provider == "ollama":
        return OllamaProvider(
            model=config.model,
            base_url=config.base_url or DEFAULT_OLLAMA_BASE_URL,
        )

    raise ValueError(f"Provider LLM nao suportado: {config.provider}")
```

A factory é chamada a cada requisição de chat (`llm_service.generate_answer`), lendo a configuração do ambiente em tempo real.

---

## Interface base

Todo provider deve implementar:

```python
# app/services/llm_providers/base.py
class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        ...
```

O método `generate` recebe o prompt completo (já formatado com histórico) e retorna a resposta do modelo como string.

---

## Configuração por provedor

### Gemini
```env
LLM_PROVIDER=gemini
LLM_MODEL=gemini-1.5-flash
LLM_API_KEY=sua-chave-gemini
```

### OpenAI
```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
LLM_API_KEY=sua-chave-openai
```

### API compatível com OpenAI (ex: LM Studio, Groq, Together)
```env
LLM_PROVIDER=openai_compatible
LLM_MODEL=nome-do-modelo
LLM_BASE_URL=https://api.exemplo.com/v1
LLM_API_KEY=chave-opcional
```

### Ollama (local)
```env
LLM_PROVIDER=ollama
LLM_MODEL=llama3.2
# LLM_BASE_URL opcional, padrão: http://localhost:11434
```

---

## Como adicionar um novo provedor

1. Criar `app/services/llm_providers/meu_provider.py` com uma classe que estende `LLMProvider` e implementa `generate(prompt: str) -> str`.
2. Importar e adicionar um bloco `if provider == "meu_provider":` em `factory.py`.
3. Documentar as variáveis de ambiente necessárias no `.env.example`.
