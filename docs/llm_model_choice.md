# Escolha e configuracao do modelo LLM

## Modelo escolhido

Provider: Gemini

Modelo: gemini-2.5-flash

## Motivo tecnico da escolha

O modelo gemini-2.5-flash foi escolhido por ser adequado para uma primeira integracao de chatbot com API externa. Ele oferece boa velocidade de resposta, custo mais controlado em comparacao com modelos maiores e qualidade suficiente para fluxos conversacionais comuns.

Essa escolha tambem facilita a evolucao do projeto, porque o provider e o modelo ficam definidos por variaveis de ambiente, sem acoplar o codigo da aplicacao a um unico fornecedor.

## Variaveis de ambiente

Crie um arquivo `.env` local com base no `.env.example`:

```env
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.5-flash
LLM_API_KEY=sua_chave_real
```

O arquivo `.env` nao deve ser enviado para o Git, porque contem segredo real.

## Como trocar o modelo futuramente

Para trocar apenas o modelo Gemini:

```env
LLM_PROVIDER=gemini
LLM_MODEL=outro-modelo-gemini
LLM_API_KEY=sua_chave_real
```

Para trocar de provider, altere o provider, o modelo e a chave:

```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4.1-mini
LLM_API_KEY=sua_chave_openai
```

A aplicacao le essas configuracoes em `app/core/config.py`.

## Integracao com o servico de LLM

O servico `app/services/llm_service.py` centraliza a comunicacao com o modelo de linguagem por meio da funcao `generate_answer`.

Essa funcao recebe:

- a mensagem atual do usuario;
- o historico da sessao;
- as configuracoes de provider, modelo e chave carregadas por variaveis de ambiente.

O endpoint `POST /api/chat` salva a mensagem do usuario, busca o historico atualizado da sessao e envia esse contexto para `generate_answer`. A resposta gerada pelo LLM e salva no historico como mensagem do assistente.

## Tratamento de falhas

Se a chave `LLM_API_KEY` nao estiver configurada, se o provider nao for suportado ou se a API do LLM falhar, a aplicacao retorna uma mensagem amigavel:

```text
Não consegui gerar uma resposta agora. Tente novamente em instantes.
```

Esse comportamento evita expor detalhes tecnicos da falha para o usuario final e preserva o formato de resposta do endpoint.

## SDK utilizado

Para Gemini, o projeto usa o pacote `google-genai`, SDK oficial recomendado pela documentacao atual da API Gemini.
