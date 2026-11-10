from pathlib import Path
import json

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .rag import VigiaIA
from .report_assistant import process_report
from .chat import answer_chat_question
from .config import OLLAMA_MODEL, ROOT

app = FastAPI(
    title="VigiaIA API",
    version="1.0.0",
    description="Assistente local de mobilidade urbana com RAG e citações."
)

engine = VigiaIA()
STATIC_DIR = ROOT / "static"
RESULTS_DIR = ROOT / "avaliacao" / "resultados"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    mode: str = Field(default="agent_rag")



class ReportChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    report: dict = Field(default_factory=dict)


@app.get("/")
def home():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model": OLLAMA_MODEL,
        "modes": ["base", "rag", "agent_rag"]
    }


@app.get("/evaluation/latest")
def latest_evaluation():
    files = list(RESULTS_DIR.glob("*.json"))
    if not files:
        raise HTTPException(
            status_code=404,
            detail="Nenhum resultado de avaliação foi encontrado."
        )

    latest = max(files, key=lambda item: item.stat().st_mtime)
    try:
        data = json.loads(latest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=500,
            detail="Não foi possível ler o resultado da avaliação."
        ) from exc

    return {"filename": latest.name, "data": data}


@app.post("/ask")
def ask(payload: AskRequest):
    try:
        return engine.ask(payload.question, payload.mode)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/chat-ask")
def chat_ask(payload: AskRequest):
    try:
        return answer_chat_question(
            payload.question,
            payload.mode,
            engine
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/report-chat")
def report_chat(payload: ReportChatRequest):
    try:
        return process_report(payload.message, payload.report)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
