# Ficha Técnica — VigiaIA

- Disciplina: Generative AI for Engineering
- Tema: Mobilidade Urbana
- Equipe: Deivison Pertel (RM 550803), Eduardo Akira Murata (RM 98713), Wesley Souza de Oliveira (RM 97874).

## Problema e objetivo
Conhecimento sobre o VigiaVia e seus fluxos está distribuído em documentação. O VigiaIA organiza esse conteúdo e permite consultas naturais com rastreabilidade.

## O que a IA faz
Responde dúvidas técnicas com base documental; recupera trechos TF-IDF; gera JSON com citações; deve se abster sem evidência; compara LLM base, RAG e agente RAG.

## O que não faz
Não detecta buracos em imagens, não substitui YOLO26n, não executa reparos, não abre chamados municipais e não toma decisões operacionais.

## Modelo
LLM local via Ollama; sugestão inicial `qwen2.5:0.5b`. Agente especializado por instruções/fluxo, não fine-tuning LoRA.

## Base
Sínteses documentais do MVP e RPA. RDD2022 é dataset de imagens, não indexado como texto.

## Avaliação
12 perguntas; Recall@1, Recall@3, JSON válido, citações, recusas e latência. Resultados devem ser medidos e registrados sem estimativas fictícias.

## Riscos
TF-IDF pode falhar em paráfrases; corpus incompleto reduz cobertura; modelo pequeno pode gerar JSON inválido; GPU de 4 GB pode exigir CPU/RAM. Revisão humana obrigatória.
