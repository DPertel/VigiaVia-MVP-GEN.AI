# VigiaIA — Assistente Inteligente de Mobilidade Urbana

Projeto acadêmico FIAP — Generative AI for Engineering — Mobilidade Urbana.

O VigiaIA responde perguntas técnicas sobre mobilidade urbana e o ecossistema VigiaVia usando documentos da equipe, recuperação RAG, modelo local via Ollama, citações e recusa quando não há evidência.

> Este pacote é uma base funcional inicial. As sínteses em `base/fontes/` foram construídas a partir de informações já compartilhadas pela equipe e devem ser conferidas com os documentos originais. Nenhuma métrica foi inventada.

## Integrantes
- Deivison Pertel — RM 550803
- Eduardo Akira Murata — RM 98713
- Wesley Souza de Oliveira — RM 97874

Confira nomes e RMs antes de publicar.

## Requisitos
- Python 3.10+ (recomendado 3.11)
- Ollama instalado e em execução
- Modelo local: sugestão inicial `qwen2.5:0.5b`
- GPU com 4 GB VRAM: começar com modelo pequeno; Ollama pode recorrer à CPU/RAM.

## Instalação (PowerShell)
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
Copy-Item .env.example .env
ollama pull qwen2.5:0.5b
ollama list
```

## Executar
```powershell
uvicorn src.api:app --host 127.0.0.1 --port 8000 --reload
```
Abra `http://127.0.0.1:8000/docs`. Saúde: `http://127.0.0.1:8000/health`.

Exemplo:
```powershell
$body = @{ question = "Qual é o objetivo do VigiaVia?"; mode = "agent_rag" } | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:8000/ask -Method Post -ContentType "application/json" -Body $body
```

## Três configurações
- `base`: LLM sem RAG.
- `rag`: RAG lexical TF-IDF.
- `agent_rag`: RAG com política estrita, JSON, validação de citação e recusa.
O agente é especializado por instruções e fluxo de controle; não é fine-tuning LoRA.

## Resultados da avalia??o

Avalia??o experimental com 12 perguntas e tr?s configura??es, utilizando `qwen2.5:0.5b`.

| Indicador | Base | RAG | Agent + RAG |
|---|---:|---:|---:|
| Execu??es bem-sucedidas | 10/12 | 12/12 | 12/12 |
| JSON v?lido | 100% | 100% | 100% |
| Cobertura de cita??es | N/A | 91,67% | 91,67% |
| Refer?ncias v?lidas entre as citadas | N/A | 100% | 100% |
| Recusas corretas | 100% | 100% | 100% |
| Completude dos termos esperados | 0% | 36,36% | 100% |
| Lat?ncia m?dia | 32,603 s | 2,492 s | 0,225 s |

Recall@1 e Recall@3: **100%** em 11 casos eleg?veis. O caso QA010, sem fonte esperada na base, foi exclu?do do c?lculo.

A Base apresentou dois erros de execu??o por indisponibilidade do Ollama. A validade das refer?ncias considera apenas os 11 casos com cita??es. A lat?ncia do Agent + RAG ? influenciada por regras determin?sticas e n?o representa somente gera??o pelo LLM.

O recuperador combina 65% de similaridade TF-IDF e 35% de sobreposi??o de termos, retornando at? tr?s trechos. O sistema aplica MIN_RELEVANCE=0.03 como limiar m?nimo de relev?ncia. Esse valor est? implementado, mas ainda n?o foi calibrado experimentalmente. O agente utiliza instru??es e regras determin?sticas, n?o LoRA.

**Relat?rio completo:** [docs/relatorio_final.md](docs/relatorio_final.md).

**An?lise experimental:** [notebooks/analise_avaliacao_vigiaia.ipynb](notebooks/analise_avaliacao_vigiaia.ipynb).

**Cinco erros reais:** [avaliacao/erros_reais.md](avaliacao/erros_reais.md).

**Cat?logo da base:** [base/catalogo_fontes.csv](base/catalogo_fontes.csv).
## Estrutura
`base/fontes/` documentos; `base/catalogo_fontes.csv` catálogo; `avaliacao/` gabarito e resultados; `docs/` ficha e arquitetura; `src/` aplicação; `tests/` testes; `notebooks/` análises.

## Fontes e limites
RDD2022 é dataset de imagens de visão computacional, não corpus textual pronto para RAG. A licença CC BY-SA 4.0 foi informada pela equipe e deve ser verificada na fonte oficial. A API do MVP não deve ser descrita como integrada a operação municipal real. O RPA usa SQLite local demonstrativo, não integração de produção.

Repositório MVP informado: https://github.com/akiramrt/vigiavia-mvp

## Checklist de entrega
- [x] Estruturar a base textual e catalogar as fontes.
- [x] Criar conjunto de teste e gabarito, incluindo caso sem evid?ncia.
- [x] Medir Recall@1 e Recall@3.
- [x] Comparar Base, RAG e Agent + RAG.
- [x] Registrar placar e cinco erros reais com corre??es propostas.
- [x] Criar ficha t?cnica, arquitetura e relat?rio consolidado.
- [x] Executar notebook e salvar as sa?das.
- [ ] Validar nomes/RMs, documentos originais, atribui??o e licen?as.
- [ ] Adicionar prints reais em `docs/evidencias/`.
- [ ] Publicar reposit?rio e v?deo; inserir links reais.