from .retriever import Retriever
from .generator import answer_question
class VigiaIA:
    def __init__(self):
        self.retriever = Retriever()
    def ask(self, question, mode="agent_rag"):
        if mode not in {"base", "rag", "agent_rag"}:
            raise ValueError("mode deve ser base, rag ou agent_rag")
        result, retrieved = answer_question(question, mode, self.retriever)
        return {"mode": mode, **result, "retrieved": [
            {k: v for k, v in item.items() if k != "text"} for item in retrieved]}
