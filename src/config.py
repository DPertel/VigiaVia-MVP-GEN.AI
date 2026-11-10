import os
from pathlib import Path
from dotenv import load_dotenv
ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b")
TOP_K = int(os.getenv("TOP_K", "3"))
MIN_RELEVANCE = float(os.getenv("MIN_RELEVANCE", "0.03"))
SOURCES_DIR = ROOT / "base" / "fontes"
