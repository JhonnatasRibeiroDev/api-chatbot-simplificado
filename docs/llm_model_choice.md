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

O provider padrao do projeto e Gemini com o modelo `gemini-2.5-flash`.

Hoje o codigo possui integracao real apenas com Gemini. Por isso, trocar entre modelos Gemini exige mudar somente variaveis no `.env`. Trocar para OpenAI, Claude, Ollama ou outro provider exige adicionar um provider/adaptador no codigo antes.

### Trocar apenas o modelo Gemini

Altere somente `LLM_MODEL` no `.env`:

```env
LLM_PROVIDER=gemini
LLM_MODEL=outro-modelo-gemini
LLM_API_KEY=sua_chave_real
```

Exemplo:

```env
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.5-pro
LLM_API_KEY=sua_chave_real
```

Depois reinicie a API para carregar a nova configuracao.

### Trocar de provider externo

Para trocar para outro provider, como OpenAI ou Claude, a configuracao futura seria parecida com:

```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4.1-mini
LLM_API_KEY=sua_chave_openai
```

Mas, no estado atual do projeto, essa troca ainda retornara a mensagem amigavel de falha porque o `llm_service.py` suporta apenas Gemini.

### Testar modelos locais no futuro

Modelos locais podem ser integrados futuramente com um provider proprio, por exemplo `ollama` ou `openai_compatible`.

Exemplo futuro com Ollama:

```env
LLM_PROVIDER=ollama
LLM_MODEL=llama3.1
LLM_API_KEY=
LLM_BASE_URL=http://localhost:11434
```

Exemplo futuro com LM Studio ou outro servidor compativel com OpenAI:

```env
LLM_PROVIDER=openai_compatible
LLM_MODEL=nome-do-modelo-local
LLM_API_KEY=local
LLM_BASE_URL=http://localhost:1234/v1
```

Para esse tipo de troca ficar desacoplada, o proximo passo arquitetural seria separar `llm_service.py` em providers/adapters, mantendo `generate_answer` como ponto unico de entrada.

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
