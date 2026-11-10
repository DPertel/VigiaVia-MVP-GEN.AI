# Cinco erros reais observados

**Fonte das evidências:** `avaliacao/resultados/avaliacao-20261110-152046.json` \
**Gabarito:** `avaliacao/gabarito.json` \
**Conjunto de perguntas:** `avaliacao/conjunto_teste.json`

Os cinco casos abaixo foram selecionados a partir de saídas efetivamente registradas na avaliação. As respostas esperadas seguem os termos e as fontes definidos no gabarito.

| ID | Caso/pergunta | Saída observada | Tipo | Causa analisada | Correção proposta | Evidência |
|---|---|---|---|---|---|---|
| E01 | QA005 — Qual licença foi informada para o RDD2022? (Base) | "Sim, o RDD2022 foi informado com a licença MIT." | Alucinação | O modelo respondeu sem consultar a base e confundiu ou inventou a licença do dataset. | Exigir evidência documental para licenças e recusar respostas sem fonte. | Resultado JSON, execução 13; gabarito QA005: `CC BY-SA 4.0`. |
| E02 | QA006 — Qual é o raio padrão de deduplicação do RPA? (Base) | "O raio padrão de deduplicação do RPA é 100% (100%)." | Alucinação | O modelo não recuperou a informação técnica e gerou um valor sem unidade ou fundamento. | Recuperar o trecho técnico do RPA e validar a presença do valor `20 metros` e do método `Haversine`. | Resultado JSON, execução 16; gabarito QA006. |
| E03 | QA008 — Qual banco local é usado pelo consumidor RPA? (Base) | "O banco local usado pelo consumidor RPA é o Banco Central do Brasil (BCB)." | Alucinação | O modelo interpretou incorretamente a pergunta e produziu uma entidade sem relação com a implementação documentada. | Restringir respostas técnicas ao contexto recuperado e validar entidades e termos esperados. | Resultado JSON, execução 22; gabarito QA008: `SQLite` e `mvp_consumer.sqlite3`. |
| E04 | QA009 — A API do MVP armazena as imagens enviadas? (RAG) | "Sim. A API do MVP armazena as imagens enviadas." | Resposta incorreta / contradição documental | Apesar de utilizar RAG e apresentar citação, a geração produziu uma afirmação contrária ao conteúdo esperado na documentação. | Melhorar a instrução de geração para considerar negações e exigir que a resposta seja consistente com o trecho citado. | Resultado JSON, execução 26; citação `VIGIAVIA_MVP_SINTESE-006`; gabarito QA009: `não armazena`. |
| E05 | QA011 — O MVP está integrado a sistema municipal real em produção? (RAG) | "Sim. O MVP está integrado a sistema municipal real em produção." | Alucinação / ausência de recusa adequada | O modelo afirmou uma integração em produção sem evidência documental suficiente, mesmo com recuperação de trechos. | Aplicar regra de abstenção ou resposta negativa fundamentada quando a documentação não confirma integração em produção. | Resultado JSON, execução 32; citação `VIGIAVIA_MVP_SINTESE-006`; gabarito QA011: `não há evidência` ou `não foi indicada integração`. |

## Outras ocorrências observadas

Estas ocorrências foram registradas, mas não foram incluídas entre os cinco erros principais:

- **QA012 — RAG:** a resposta listou `id`, `data`, `latitude`, `longitude` e `gravidade`, mas omitiu `descricao`, exigido pelo gabarito. Classificação: resposta incompleta. Evidência: execução 35.
- **QA010 — Base:** falha de acesso ao Ollama após 182,028 segundos. Classificação: erro de execução, não erro de conteúdo. Evidência: execução 28.
- **QA012 — Base:** falha de acesso ao Ollama após 182,044 segundos. Classificação: erro de execução, não erro de conteúdo. Evidência: execução 34.

## Interpretação

Os casos mostram que a geração Base está mais exposta a respostas sem fundamentação documental. O RAG melhora o acesso às fontes, mas não elimina erros: nos casos QA009 e QA011, o modelo apresentou afirmações incorretas mesmo com referências recuperadas.

O Agent + RAG apresentou respostas alinhadas ao gabarito nesses casos específicos, conforme as execuções correspondentes do mesmo arquivo. Isso não significa que o agente seja infalível; os resultados devem ser interpretados dentro do conjunto de testes utilizado.

As correções propostas são melhorias a validar em uma nova execução da avaliação. Não representam resultados já comprovados.
