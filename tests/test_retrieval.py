from src.retriever import Retriever
def test_retriever_returns_chunks():
    result = Retriever().search("Qual é o objetivo do VigiaVia?", 3)
    assert result
    assert result[0]["source_id"] == "VIGIAVIA_MVP_SINTESE"
