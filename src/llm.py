import requests
from .config import OLLAMA_BASE_URL, OLLAMA_MODEL
class OllamaError(RuntimeError):
    pass
def generate(prompt, model=None, temperature=0.1):
    payload = {"model": model or OLLAMA_MODEL, "prompt": prompt, "stream": False,
               "options": {"temperature": temperature}}
    try:
        response = requests.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload, timeout=180)
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except requests.RequestException as exc:
        raise OllamaError(f"Não foi possível acessar o Ollama em {OLLAMA_BASE_URL}. "
                          "Verifique se está aberto e se o modelo foi baixado.") from exc
