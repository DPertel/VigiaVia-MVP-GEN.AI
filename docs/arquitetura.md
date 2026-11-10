# Arquitetura

```mermaid
flowchart TD
 U[Usuário] --> API[FastAPI]
 API --> M{Modo}
 M -->|base| LLM[Ollama local]
 M -->|rag| R[TF-IDF Retriever]
 M -->|agent_rag| A[Política do agente]
 A --> R
 R --> KB[Markdown da base]
 R --> C[Top-k trechos e IDs]
 C --> LLM
 LLM --> V[Validação JSON e citações]
 V --> O[Resposta JSON]
```

1. Usuário envia pergunta/modo.
2. Base chama o modelo sem recuperação; RAG recupera trechos; agente RAG aplica política estrita.
3. TF-IDF seleciona até três trechos.
4. Prompt inclui evidências e identificadores.
5. Ollama gera resposta JSON; o sistema valida estrutura e filtra citações.

A aplicação é local e demonstrativa. Não exponha publicamente sem autenticação, limites de requisição e controles de privacidade.
