# VigiaIA — Assistente Inteligente de Mobilidade Urbana

Projeto acadêmico FIAP — Generative AI for Engineering — Mobilidade Urbana.

O VigiaIA responde a perguntas técnicas sobre mobilidade urbana e o ecossistema VigiaVia utilizando documentos da equipe, recuperação RAG, modelo local via Ollama, citações e recusa quando não há evidências suficientes.

> Este pacote é uma base funcional inicial. As sínteses em `base/fontes/` foram construídas a partir de informações já compartilhadas pela equipe e devem ser conferidas com os documentos originais. Nenhuma métrica foi inventada.

## Integrantes

- Deivison Pertel — RM 550803
- Eduardo Akira Murata — RM 98713
- Wesley Souza de Oliveira — RM 97874

- Video referente ao projeto: https://youtu.be/61MAQKuJZdk

## Requisitos

- Python 3.10 ou superior (recomendado: 3.11).
- Ollama instalado e em execução.
- Modelo local: `qwen2.5:0.5b`.
- GPU com 4 GB de VRAM: recomenda-se começar com um modelo pequeno. O Ollama pode recorrer à CPU e à RAM quando necessário.

## Instalação (PowerShell)

Execute os comandos abaixo, um por vez, no terminal:

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

Com o ambiente virtual ativado e o Ollama em execução:

```powershell
uvicorn src.api:app --host 127.0.0.1 --port 8000 --reload
```

Abra a aplicação:

- Interface: http://127.0.0.1:8000
- Documentação da API: http://127.0.0.1:8000/docs
- Verificação de saúde: http://127.0.0.1:8000/health

### Exemplo de consulta à API

```powershell
$body = @{
    question = "Qual é o objetivo do VigiaVia?"
    mode = "agent_rag"
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/ask" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

## Três configurações avaliadas

- `base`: LLM sem RAG.
- `rag`: RAG lexical com TF-IDF.
- `agent_rag`: RAG com política estrita, resposta estruturada em JSON, validação de citações e recusa quando não há evidências suficientes.

O agente é especializado por instruções e fluxo de controle. Não foi realizado fine-tuning LoRA.

## Resultados da avaliação

Avaliação experimental com 12 perguntas e três configurações, utilizando `qwen2.5:0.5b`.

| Indicador | Base | RAG | Agent + RAG |
|---|---:|---:|---:|
| Execuções bem-sucedidas | 10/12 | 12/12 | 12/12 |
| JSON válido | 100% | 100% | 100% |
| Cobertura de citações | N/A | 91,67% | 91,67% |
| Referências válidas entre as citadas | N/A | 100% | 100% |
| Recusas corretas | 100% | 100% | 100% |
| Completude dos termos esperados | 0% | 36,36% | 100% |
| Latência média | 32,603 s | 2,492 s | 0,225 s |

**Recall@1 e Recall@3:** 100% nos 11 casos elegíveis. O caso QA010, sem fonte esperada na base, foi excluído do cálculo.

A configuração Base apresentou dois erros de execução por indisponibilidade do Ollama. A validade das referências considera apenas os 11 casos com citações.

A latência do Agent + RAG é influenciada por regras determinísticas e não representa somente o tempo de geração pelo LLM.

### Recuperação e relevância

O recuperador combina 65% de similaridade TF-IDF e 35% de sobreposição de termos, retornando até três trechos.

O sistema aplica `MIN_RELEVANCE=0.03` como limiar mínimo de relevância. Esse valor está implementado, mas ainda não foi calibrado experimentalmente.

O agente utiliza instruções e regras determinísticas, não LoRA.

## Documentação e evidências

- **Relatório completo:** [docs/relatorio_final.md](docs/relatorio_final.md)
- **Análise experimental:** [notebooks/analise_avaliacao_vigiaia.ipynb](notebooks/analise_avaliacao_vigiaia.ipynb)
- **Cinco erros reais:** [avaliacao/erros_reais.md](avaliacao/erros_reais.md)
- **Catálogo da base:** [base/catalogo_fontes.csv](base/catalogo_fontes.csv)

## Estrutura do projeto

```text
base/
  fontes/
  catalogo_fontes.csv
avaliacao/
  conjunto_teste.json
  gabarito.json
  erros_reais.md
  placar.csv
docs/
  arquitetura.md
  ficha_tecnica.md
  relatorio_final.md
notebooks/
  analise_avaliacao_vigiaia.ipynb
src/
static/
tests/
```

## Fontes e limitações

O RDD2022 é um dataset de imagens de visão computacional, não um corpus textual pronto para RAG. A licença CC BY-SA 4.0 foi informada pela equipe e deve ser verificada na fonte oficial.

A API do MVP não deve ser descrita como integrada a uma operação municipal real. O RPA utiliza SQLite local em caráter demonstrativo, sem integração de produção.

Repositório do MVP de referência informado pela equipe:

https://github.com/akiramrt/vigiavia-mvp

## Repositório do projeto

https://github.com/DPertel/VigiaVia-MVP-GEN.AI