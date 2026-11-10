# Relat?rio T?cnico Final ? VigiaIA

**Disciplina:** Generative AI for Engineering \
**Tema:** Mobilidade Urbana \
**Projeto:** VigiaIA ? Assistente Inteligente de Mobilidade Urbana

## 1. Integrantes

- Deivison Pertel ? RM 550803
- Eduardo Akira Murata ? RM 98713
- Wesley Souza de Oliveira ? RM 97874

## 2. Problema e tarefa da IA

O VigiaIA ? um assistente de consulta t?cnica sobre o ecossistema VigiaVia. A tarefa ? responder perguntas em linguagem natural usando documenta??o da equipe, recuperar evid?ncias, apresentar identificadores de fontes e abster-se quando n?o houver informa??o suficiente.

O sistema n?o detecta buracos em imagens, n?o substitui o YOLO26n, n?o executa reparos e n?o abre chamados em sistemas municipais. ? uma aplica??o acad?mica local e demonstrativa.

## 3. Pipeline de IA

1. Usu?rio envia pergunta e seleciona uma configura??o.
2. A API FastAPI direciona a solicita??o para Base, RAG ou Agent + RAG.
3. O RAG consulta os documentos Markdown divididos em trechos.
4. O recuperador TF-IDF combina similaridade textual e sobreposi??o de termos.
5. Os trechos e identificadores s?o enviados ao modelo local Ollama.
6. A aplica??o valida a estrutura JSON e as refer?ncias retornadas.
7. O sistema apresenta resposta, cita??es ou absten??o.

Diagrama detalhado: [docs/arquitetura.md](arquitetura.md).

## 4. Base de conhecimento

O corpus textual cont?m 15 trechos: 9 da s?ntese do MVP e 6 da s?ntese do RPA.

| Fonte | Formato | Licen?a informada | Trechos | Uso |
|---|---|---|---:|---|
| S?ntese VigiaVia MVP | Markdown | A verificar na fonte original | 9 | RAG |
| S?ntese VigiaVia RPA | Markdown | Autoria da equipe; verificar depend?ncias | 6 | RAG |
| RDD2022 | Dataset de imagens | CC BY-SA 4.0 informada pela equipe; confirmar oficialmente | 0 | N?o integra o corpus textual |

As duas s?nteses foram organizadas a partir de informa??es compartilhadas pela equipe e n?o substituem os documentos originais. O RDD2022 ? um dataset visual, n?o um corpus textual do RAG.

Cat?logo completo: [base/catalogo_fontes.csv](../base/catalogo_fontes.csv).

## 5. Recupera??o e metodologia

O recuperador utiliza TF-IDF com unigramas e bigramas. A pontua??o combina:

- 65% de similaridade TF-IDF;
- 35% de cobertura dos termos importantes da pergunta.

S?o retornados at? tr?s trechos (Top-3). A escolha de tr?s permite fornecer contexto complementar sem ampliar excessivamente o contexto enviado ao modelo.

**Limiar implementado:** o sistema aplica `MIN_RELEVANCE=0.03` ? pontua??o do primeiro trecho recuperado. Se n?o houver trechos ou se a maior pontua??o ficar abaixo desse valor, o sistema se abst?m de responder. O Top-3 define a quantidade m?xima de trechos recuperados, enquanto `MIN_RELEVANCE` define o limiar m?nimo de aceita??o. **Limita??o experimental:** o valor 0.03 est? implementado, mas ainda n?o foi calibrado sistematicamente em conjunto de valida??o para comparar falsos positivos e falsos negativos.

### Resultado da recupera??o

| M?trica | Resultado |
|---|---:|
| Casos eleg?veis | 11 |
| Casos sem fonte esperada, exclu?dos | 1 |
| Recall@1 | 100% |
| Recall@3 | 100% |

O QA010, cuja resposta n?o consta na base, foi exclu?do do c?lculo de recall por n?o possuir fonte esperada. O resultado mede recupera??o da fonte esperada, n?o corre??o sem?ntica da resposta gerada.

## 6. Compara??o das configura??es

Modelo utilizado: `qwen2.5:0.5b`, executado localmente via Ollama.

| Indicador | Base | RAG | Agent + RAG |
|---|---:|---:|---:|
| Execu??es bem-sucedidas | 10/12 | 12/12 | 12/12 |
| Erros de execu??o | 2 | 0 | 0 |
| JSON v?lido | 100% | 100% | 100% |
| Cobertura de cita??es | N/A | 91,67% | 91,67% |
| Refer?ncias v?lidas entre casos citados | N/A | 100% (11/11) | 100% (11/11) |
| Recusas corretas | 100% | 100% | 100% |
| Completude dos termos esperados | 0% | 36,36% | 100% |
| Lat?ncia m?dia | 32,603 s | 2,492 s | 0,225 s |
| Lat?ncia mediana | 2,445 s | 2,684 s | 0,002 s |

A cobertura de cita??es de 91,67% corresponde a 11 dos 12 casos. A validade de refer?ncias de 100% considera somente as 11 respostas que apresentaram cita??es. Isso n?o comprova, por si s?, que cada cita??o sustenta semanticamente toda a resposta.

A configura??o Base teve duas falhas de execu??o por indisponibilidade do Ollama nos casos QA010 e QA012. A m?dia de lat?ncia foi afetada por esses timeouts. N?o devem ser interpretadas como falhas de conte?do.

O Agent + RAG apresentou completude de termos esperados de 100% neste conjunto. Sua implementa??o cont?m regras determin?sticas e fluxo de controle; portanto, a lat?ncia m?dia n?o representa exclusivamente tempo de gera??o do LLM. O agente ? uma especializa??o por instru??es e regras, n?o LoRA ou fine-tuning.

**Interpreta??o:** o RAG melhorou a fundamenta??o e reduziu erros de execu??o observados em rela??o ? Base, mas n?o eliminou contradi??es. O Agent + RAG apresentou maior ader?ncia ao gabarito neste conjunto de 12 perguntas. O resultado n?o garante desempenho equivalente em perguntas fora do conjunto avaliado.

## 7. Cinco erros reais e corre??es propostas

Os cinco casos foram registrados em [avaliacao/erros_reais.md](../avaliacao/erros_reais.md), com sa?da observada, causa, proposta de corre??o e refer?ncia ? execu??o.

| Caso | Configura??o | Erro observado | Corre??o proposta |
|---|---|---|---|
| QA005 | Base | Inventou licen?a MIT para o RDD2022 | Exigir evid?ncia documental para licen?as e abster-se sem fonte |
| QA006 | Base | Informou raio de deduplica??o de 100% | Recuperar e validar valor de 20 metros e m?todo Haversine |
| QA008 | Base | Respondeu Banco Central em vez de SQLite | Restringir respostas t?cnicas ao contexto recuperado |
| QA009 | RAG | Afirmou que a API armazena imagens, contrariando a fonte | Tratar nega??es e validar consist?ncia com o trecho citado |
| QA011 | RAG | Afirmou integra??o municipal em produ??o sem evid?ncia | Aplicar absten??o quando a documenta??o n?o confirma integra??o |

As corre??es s?o propostas e ainda precisam ser validadas em nova avalia??o.

## 8. Conclus?o t?cnica

O experimento mostra que a recupera??o documental melhora a rastreabilidade em compara??o ? gera??o sem contexto, mas n?o elimina alucina??es nem contradi??es. O agente com RAG apresentou maior completude dos termos esperados no conjunto testado, apoiado por regras determin?sticas e valida??es.

As principais limita??es s?o o corpus pequeno, composto por apenas 15 trechos derivados de duas s?nteses da equipe; a aus?ncia de limiar m?nimo de relev?ncia calibrado; o modelo compacto; e a necessidade de revis?o humana das respostas. A validade estrutural do JSON n?o deve ser confundida com verdade factual.

Como pr?ximos passos t?cnicos, recomenda-se ampliar e validar as fontes originais, calibrar um limiar com conjunto independente, testar par?frases e perguntas adversariais, avaliar entailment das cita??es e repetir os testes em m?ltiplas execu??es.

## 9. Reprodutibilidade e links

- Reposit?rio do projeto: https://github.com/DPertel/VigiaVia-MVP-GEN.AI
- Reposit?rio MVP de refer?ncia: https://github.com/akiramrt/vigiavia-mvp
- V?deo de apresenta??o: **inserir link ap?s publica??o**.
- README com instala??o e execu??o: [README.md](../README.md).
- Notebook de an?lise: [analise_avaliacao_vigiaia.ipynb](../notebooks/analise_avaliacao_vigiaia.ipynb).
- Evid?ncia da avalia??o: [avaliacao-20261110-152046.json](evidencias/avaliacao-20261110-152046.json).
