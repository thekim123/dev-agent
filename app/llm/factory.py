from app.llm.embedder import Embedder
from app.llm.llm_client import LLMClient


def create_embedder():
    return Embedder()


def create_llm_client():
    return LLMClient()
