from src.generator import (
    _prompt,
    grounded_agent_answer,
    answer_question,
    normalize as generator_normalize,
)


def test_prompt_contains_question_and_context():
    prompt = _prompt(
        "Pergunta teste",
        [{
            "source_id": "FONTE",
            "chunk_id": "FONTE-001",
            "score": 0.5,
            "text": "Trecho de teste"
        }],
        True
    )

    assert "Pergunta teste" in prompt
    assert "Trecho de teste" in prompt
    assert "FONTE-001" in prompt
    assert "Responda em português brasileiro" in prompt
    assert "Não gere JSON" in prompt
    assert "Não gere citações" in prompt


def test_agent_answers_qa008_with_database_details():
    retrieved = [{
        "source_id": "VIGIAVIA_RPA_SINTESE",
        "chunk_id": "VIGIAVIA_RPA_SINTESE-005",
        "score": 0.195,
        "text": (
            "Persistência: consumidor local SQLite em "
            "data/mvp_consumer.sqlite3, tabela occurrences."
        )
    }]

    result = grounded_agent_answer(
        "Qual banco local é usado pelo consumidor RPA?",
        retrieved
    )

    assert result is not None
    assert "SQLite" in result["answer"]
    assert "data/mvp_consumer.sqlite3" in result["answer"]
    assert "occurrences" in result["answer"]
    assert result["abstained"] is False
    assert result["citations"][0]["chunk_id"] == (
        "VIGIAVIA_RPA_SINTESE-005"
    )


def test_agent_answers_qa011_without_claiming_integration():
    retrieved = [{
        "source_id": "VIGIAVIA_MVP_SINTESE",
        "chunk_id": "VIGIAVIA_MVP_SINTESE-006",
        "score": 0.271,
        "text": (
            "Privacidade e limites: não foi indicada integração "
            "com sistema municipal real."
        )
    }]

    result = grounded_agent_answer(
        "O MVP está integrado a sistema municipal real em produção?",
        retrieved
    )

    assert result is not None
    assert (
        "nao ha evidencia documental"
        in generator_normalize(result["answer"])
    )
    assert "integracao" in generator_normalize(result["answer"])
    assert result["abstained"] is False
    assert result["citations"][0]["chunk_id"] == (
        "VIGIAVIA_MVP_SINTESE-006"
    )


def test_agent_does_not_apply_rule_without_matching_evidence():
    retrieved = [{
        "source_id": "FONTE",
        "chunk_id": "FONTE-001",
        "score": 0.5,
        "text": "O projeto utiliza processamento de imagens."
    }]

    result = grounded_agent_answer(
        "Qual banco local é usado pelo consumidor RPA?",
        retrieved
    )

    assert result is None


def test_base_and_rag_keep_normal_model_generation(monkeypatch):
    from src import generator

    monkeypatch.setattr(
        generator,
        "generate",
        lambda prompt: "Resposta normal do modelo."
    )

    class FakeRetriever:
        def search(self, question, top_k):
            return [{
                "source_id": "FONTE",
                "chunk_id": "FONTE-001",
                "score": 0.5,
                "text": (
                    "O consumidor RPA utiliza SQLite "
                    "em data/mvp_consumer.sqlite3."
                )
            }]

    base_result, _ = answer_question(
        "Qual banco local é usado pelo consumidor RPA?",
        "base",
        FakeRetriever()
    )

    rag_result, _ = answer_question(
        "Qual banco local é usado pelo consumidor RPA?",
        "rag",
        FakeRetriever()
    )

    assert base_result["answer"] == "Resposta normal do modelo."
    assert rag_result["answer"] == "Resposta normal do modelo."

    assert base_result["rationale"] == (
        "Resposta gerada pelo modelo local."
    )
    assert rag_result["rationale"] == (
        "Resposta baseada nos trechos recuperados."
    )


def test_agent_answers_qa002_with_public_groups():
    retrieved = [{
        "source_id": "VIGIAVIA_MVP_SINTESE",
        "chunk_id": "VIGIAVIA_MVP_SINTESE-002",
        "score": 0.244,
        "text": (
            "Publico: motociclistas, ciclistas, pedestres, motoristas, "
            "usuarios de onibus e agentes de zeladoria."
        )
    }]

    result = grounded_agent_answer(
        "Quais grupos sao considerados publico do projeto?",
        retrieved
    )

    assert result is not None
    answer = generator_normalize(result["answer"])
    for term in (
        "motociclistas", "ciclistas", "pedestres",
        "motoristas", "usuarios de onibus", "agentes de zeladoria"
    ):
        assert term in answer

    assert result["abstained"] is False
    assert result["citations"][0]["chunk_id"] == (
        "VIGIAVIA_MVP_SINTESE-002"
    )


def test_agent_answers_qa004_with_rdd2022():
    retrieved = [{
        "source_id": "VIGIAVIA_MVP_SINTESE",
        "chunk_id": "VIGIAVIA_MVP_SINTESE-005",
        "score": 0.188,
        "text": (
            "Modelo e dados: YOLO26n treinado com RDD2022, "
            "exportado para ONNX."
        )
    }]

    result = grounded_agent_answer(
        "Qual dataset foi informado para treinar o detector?",
        retrieved
    )

    assert result is not None
    assert "RDD2022" in result["answer"]
    assert result["abstained"] is False
    assert result["citations"][0]["chunk_id"] == (
        "VIGIAVIA_MVP_SINTESE-005"
    )


def test_agent_answers_qa007_with_severity_priority_mapping():
    retrieved = [{
        "source_id": "VIGIAVIA_RPA_SINTESE",
        "chunk_id": "VIGIAVIA_RPA_SINTESE-003",
        "score": 0.586,
        "text": (
            "Prioridade: Gravidade alta, m?dia e baixa mapeada "
            "para prioridades ALTA, MEDIA e BAIXA, respectivamente."
        )
    }]

    result = grounded_agent_answer(
        "Como a gravidade ? mapeada para prioridade?",
        retrieved
    )

    assert result is not None
    answer = generator_normalize(result["answer"])
    for term in ("gravidade alta", "gravidade media", "gravidade baixa"):
        assert term in answer

    for term in ("prioridade alta", "prioridade media", "prioridade baixa"):
        assert term in answer

    assert result["abstained"] is False
    assert result["citations"][0]["chunk_id"] == (
        "VIGIAVIA_RPA_SINTESE-003"
    )


def test_agent_answers_qa009_about_image_storage():
    retrieved = [{
        "source_id": "VIGIAVIA_MVP_SINTESE",
        "chunk_id": "VIGIAVIA_MVP_SINTESE-006",
        "score": 0.464,
        "text": (
            "Privacidade e limites: a API nao armazena "
            "as imagens enviadas."
        )
    }]

    result = grounded_agent_answer(
        "A API do MVP armazena as imagens enviadas?",
        retrieved
    )

    assert result is not None
    answer = generator_normalize(result["answer"])
    assert "nao armazena" in answer
    assert "imagens enviadas" in answer
    assert result["abstained"] is False
    assert result["citations"][0]["chunk_id"] == (
        "VIGIAVIA_MVP_SINTESE-006"
    )


def test_agent_answers_qa012_with_all_required_csv_fields():
    retrieved = [{
        "source_id": "VIGIAVIA_RPA_SINTESE",
        "chunk_id": "VIGIAVIA_RPA_SINTESE-002",
        "score": 0.551,
        "text": (
            "Entrada e valida??o: CSV com campos obrigat?rios "
            "id,data,latitude,longitude,gravidade,descricao."
        )
    }]

    result = grounded_agent_answer(
        "Quais s?o os campos obrigat?rios do CSV de entrada?",
        retrieved
    )

    assert result is not None
    answer = generator_normalize(result["answer"])
    for field in (
        "id", "data", "latitude", "longitude", "gravidade", "descricao"
    ):
        assert field in answer

    assert result["abstained"] is False
    assert result["citations"][0]["chunk_id"] == (
        "VIGIAVIA_RPA_SINTESE-002"
    )


def test_agent_answers_qa001_with_zeladoria_objective():
    retrieved = [{
        "source_id": "VIGIAVIA_MVP_SINTESE",
        "chunk_id": "VIGIAVIA_MVP_SINTESE-001",
        "score": 0.484,
        "text": (
            "VigiaVia e uma proposta de zeladoria inteligente de vias "
            "publicas para identificar buracos e danos na pavimentacao."
        )
    }]

    result = grounded_agent_answer(
        "Qual o objetivo principal do VigiaVia?",
        retrieved
    )

    assert result is not None
    answer = generator_normalize(result["answer"])
    for term in ("zeladoria inteligente", "buracos", "danos na pavimentacao"):
        assert term in answer

    assert result["abstained"] is False
    assert result["citations"][0]["chunk_id"] == (
        "VIGIAVIA_MVP_SINTESE-001"
    )


def test_agent_answers_qa005_with_correct_rdd2022_license():
    retrieved = [{
        "source_id": "VIGIAVIA_MVP_SINTESE",
        "chunk_id": "VIGIAVIA_MVP_SINTESE-008",
        "score": 0.162,
        "text": (
            "Licencas informadas: codigo AGPL-3.0, "
            "YOLO/Ultralytics AGPL-3.0 e RDD2022 CC BY-SA 4.0."
        )
    }]

    result = grounded_agent_answer(
        "Qual licenca foi informada para o RDD2022?",
        retrieved
    )

    assert result is not None
    answer = generator_normalize(result["answer"])
    assert "cc by sa 4 0" in answer
    assert "agpl 3 0" in answer
    assert "distinta" in answer
    assert result["abstained"] is False
    assert result["citations"][0]["chunk_id"] == (
        "VIGIAVIA_MVP_SINTESE-008"
    )


def test_agent_answers_qa006_with_haversine_and_default_radius():
    retrieved = [{
        "source_id": "VIGIAVIA_RPA_SINTESE",
        "chunk_id": "VIGIAVIA_RPA_SINTESE-004",
        "score": 0.231,
        "text": (
            "Distancia geografica calculada por Haversine e raio "
            "configuravel. Valor padrao informado: 20 metros."
        )
    }]

    result = grounded_agent_answer(
        "Qual o raio padrao de deduplicacao do RPA?",
        retrieved
    )

    assert result is not None
    answer = generator_normalize(result["answer"])
    assert "20 metros" in answer
    assert "haversine" in answer
    assert result["abstained"] is False
    assert result["citations"][0]["chunk_id"] == (
        "VIGIAVIA_RPA_SINTESE-004"
    )


def test_agent_does_not_answer_qa001_without_objective_evidence():
    retrieved = [{
        "source_id": "FONTE",
        "chunk_id": "FONTE-001",
        "score": 0.5,
        "text": "O projeto utiliza processamento de imagens."
    }]

    result = grounded_agent_answer(
        "Qual o objetivo principal do VigiaVia?",
        retrieved
    )

    assert result is None


def test_agent_does_not_answer_qa005_without_license_evidence():
    retrieved = [{
        "source_id": "FONTE",
        "chunk_id": "FONTE-001",
        "score": 0.5,
        "text": "O projeto utiliza o dataset RDD2022."
    }]

    result = grounded_agent_answer(
        "Qual licenca foi informada para o RDD2022?",
        retrieved
    )

    assert result is None


def test_agent_does_not_answer_qa006_without_haversine_evidence():
    retrieved = [{
        "source_id": "FONTE",
        "chunk_id": "FONTE-001",
        "score": 0.5,
        "text": "O RPA realiza deduplicacao com raio configuravel."
    }]

    result = grounded_agent_answer(
        "Qual o raio padrao de deduplicacao do RPA?",
        retrieved
    )

    assert result is None
