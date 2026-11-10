from fastapi.testclient import TestClient
from src.api import app
client = TestClient(app)
def test_health():
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"
def test_invalid_mode():
    r = client.post("/ask", json={"question":"Pergunta válida?", "mode":"xyz"})
    assert r.status_code == 400
