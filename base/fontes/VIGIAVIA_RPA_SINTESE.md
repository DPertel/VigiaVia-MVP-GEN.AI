# Síntese documental — VigiaVia RPA

## Objetivo
Protótipo RPA para recepção, validação, classificação, deduplicação e registro local de ocorrências de buracos. Demonstra preparação de dados para consumo por outro sistema.

## Entrada e validação
CSV com campos obrigatórios `id,data,latitude,longitude,gravidade,descricao`. Validação de data ISO, coordenadas numéricas em faixas válidas e gravidade reconhecida.

## Prioridade
Gravidade alta, média e baixa mapeada para prioridades ALTA, MEDIA e BAIXA, respectivamente.

## Deduplicação
Distância geográfica calculada por Haversine e raio configurável. Valor padrão informado: 20 metros. Proximidade pode sinalizar duplicidade, conforme regras implementadas.

## Persistência
Consumidor local SQLite em `data/mvp_consumer.sqlite3`, tabela `occurrences`, chave primária `occurrence_id` e `INSERT OR IGNORE` para evitar inserções repetidas. Processamento gera relatórios CSV/JSON e logs e organiza arquivos em pendentes, processados, erros e saída.

## Testes e limites
Equipe informou 12 testes automatizados aprovados em execução anterior; reproduzir no código final antes de usar como evidência. SQLite é local/demonstrativo e não comprova integração com produção.
