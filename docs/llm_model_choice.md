# Escolha, troca e testes do modelo LLM

## Estado atual

O projeto usa uma camada de providers para chamar modelos de linguagem sem acoplar a rota de chat a um fornecedor especifico.

O fluxo atual e:

```text
POST /api/chat
  -> app/routes/chat.py
  -> app/services/session_service.py
  -> app/services/llm_service.py
  -> app/services/llm_providers/factory.py
  -> provider configurado no .env
```

O `llm_service.py` monta o prompt com:

- instrucao fixa do assistente;
- historico da sessao;
- mensagem atual do usuario.

Depois ele chama o provider ativo e registra metricas de tempo em log, incluindo tempo de criacao do provider, montagem do prompt, geracao da resposta e tempo total.

## Providers suportados

O codigo atual suporta:

- `gemini`: usa o SDK `google-genai`.
- `openai`: usa endpoint compativel com OpenAI em `https://api.openai.com/v1`.
- `openai_compatible`: usa um endpoint informado em `LLM_BASE_URL`.
- `ollama`: usa Ollama local, por padrao em `http://localhost:11434`.

## Variaveis de ambiente

Crie um arquivo `.env` local com base no `.env.example`:

```env
LLM_PROVIDER=gemini
LLM_MODEL=gemini-3.5-flash
LLM_API_KEY=sua_chave_real
LLM_BASE_URL=
```

O arquivo `.env` nao deve ser enviado para o Git, porque contem segredo real.

## Como trocar apenas o modelo

Se o provider continuar o mesmo, normalmente basta trocar `LLM_MODEL`.

Exemplo:

```env
LLM_PROVIDER=gemini
LLM_MODEL=outro-modelo-gemini
LLM_API_KEY=sua_chave_real
LLM_BASE_URL=
```

Depois reinicie a API.

Reiniciar a API significa parar o servidor atual com `Ctrl + C` e iniciar novamente:

```bash
uvicorn app.main:app --reload
```

Isso e necessario porque as variaveis do `.env` sao carregadas quando a aplicacao sobe.

## Como trocar de provider

Para trocar de fornecedor, altere `LLM_PROVIDER` e ajuste as demais variaveis.

### Gemini

```env
LLM_PROVIDER=gemini
LLM_MODEL=gemini-3.5-flash
LLM_API_KEY=sua_chave_gemini
LLM_BASE_URL=
```

### OpenAI

```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4.1-mini
LLM_API_KEY=sua_chave_openai
LLM_BASE_URL=
```

### Provider compativel com OpenAI

Use quando o servidor expuser uma API no formato `/chat/completions`.

```env
LLM_PROVIDER=openai_compatible
LLM_MODEL=nome-do-modelo
LLM_API_KEY=sua_chave_ou_local
LLM_BASE_URL=http://localhost:1234/v1
```

### Ollama

```env
LLM_PROVIDER=ollama
LLM_MODEL=llama3.1
LLM_API_KEY=
LLM_BASE_URL=http://localhost:11434
```

## Testes de desempenho feitos

Durante a avaliacao do projeto, foram feitos testes reais de tempo com chamadas sequenciais e simultaneas ao modelo configurado no `.env`.

Resultados observados depois da estabilizacao da configuracao:

- 5 requisicoes sequenciais curtas: media aproximada de 7.747s por requisicao.
- 10 requisicoes sequenciais com perguntas tecnicas: media aproximada de 3.714s por requisicao.
- 5 requisicoes simultaneas: tempo total aproximado de 4.927s para o lote, com media individual de 4.259s.

As respostas simultaneas avaliadas bateram em qualidade para perguntas sobre API, FastAPI, frontend/backend, `git fetch` vs `git pull` e fluxo HTTP.

## Observacoes sobre performance

- Prompts menores podem ajudar, mas o principal fator de latencia costuma ser o modelo/provider escolhido.
- Modelos maiores tendem a responder melhor em tarefas complexas, mas podem ser mais lentos.
- Modelos flash ou menores tendem a ser melhores para chat simples e respostas curtas.
- Requisicoes simultaneas podem reduzir o tempo total percebido, desde que o provider e o limite de requisicoes permitam.
- Se o provider tiver limite de requisicoes por minuto, evite disparar muitos testes simultaneos sem controle.

## Falhas tratadas

Se a chave estiver ausente, o provider nao for suportado ou a API externa falhar, o endpoint retorna uma mensagem amigavel:

```text
Nao consegui gerar uma resposta agora. Tente novamente em instantes.
```

Isso evita expor detalhes tecnicos para o usuario final e mantem o formato de resposta da rota.
