# Síntese documental — VigiaVia MVP

## Objetivo
VigiaVia é uma proposta de zeladoria inteligente de vias públicas para identificar buracos e danos na pavimentação. Chamados manuais podem ser lentos, imprecisos e duplicados.

## Público e piloto
Público considerado: motociclistas, ciclistas, pedestres, motoristas, usuários de ônibus e agentes de zeladoria. Piloto descrito: região central de São Paulo, com foco na Bela Vista. Dados demonstrativos devem ser identificados como simulados.

## Proposta
A proposta aproveita câmeras que já circulam pela cidade para detectar buracos, gerar relatos georreferenciados e priorizados e permitir validação humana. Não há evidência de operação municipal real conectada.

## Arquitetura
A documentação descreve API FastAPI, interface web, detector YOLO26n exportado para ONNX e execução ONNX Runtime. Infraestrutura-alvo: Azure Container Apps, Azure Container Registry, Log Analytics, Terraform, GitHub Actions, Prometheus e Grafana.

## Modelo e dados
A equipe informou YOLO26n treinado com RDD2022, exportado para ONNX, com mAP@0,5 de 0,585 no teste. Confirmar no relatório original antes de publicar como resultado definitivo. RDD2022 é dataset de imagens, não corpus textual pronto para RAG.

## Privacidade e limites
Segundo a documentação compartilhada, a API não armazena as imagens enviadas. Relatos guardam latitude, longitude, severidade e recorte da via; logs com retenção informada de 30 dias. Fila de zeladoria sem autenticação foi apontada como limitação de demonstração. Não foi indicada integração com sistema municipal real.

## Indicadores e ODS
Indicadores: tempo detecção-reparo, duplicidades evitadas, buracos por km, precisão de detecções confirmadas, disponibilidade, p95, taxa de erros e saturação. ODS relacionados: 11.2, 11.3, 9.1 e 3.6.

## Licenças informadas
A equipe informou código AGPL-3.0, YOLO/Ultralytics AGPL-3.0 e RDD2022 CC BY-SA 4.0. Conferir termos e avisos oficiais antes de redistribuir.

## Referências
Repositório informado: https://github.com/akiramrt/vigiavia-mvp
