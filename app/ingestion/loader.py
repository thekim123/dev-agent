import json
import os
from pathlib import Path

import numpy as np

from app.ingestion.chunker import DocumentChunk
from app.ingestion.embedder import Embedder

ALLOWED = (".java", ".md", ".yml", ".txt", ".properties")
EXCLUDED_DIRS = {".gradle", "gradle", ".github", "build", "target", ".git", ".idea", "node_modules", "__pycache__"}
BASE_DIR = Path(__file__).resolve().parent.parent

bedrock = Embedder()


def get_dir_list(project_root):
    documents = []
    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

        for file in files:
            if file.endswith(ALLOWED):
                path = os.path.join(root, file)

                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                # print(path)
                documents.append({
                    "content": content,
                    "path": path
                })
    return documents


def load_vector_store(path="vector_store.json"):
    vector_store_path = BASE_DIR / path
    with open(vector_store_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    chunks = []
    for item in data:
        chunk = DocumentChunk(
            chunk_id=item["chunk_id"],
            source_path=item["source_path"],
            text=item["text"],
            start=item["start"],
            end=item["end"],
            embedding=item["embedding"],
        )
        chunks.append(chunk)
    return chunks


def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def search_chunks(query_embedding, chunks, top_k=3):
    scored = []
    for chunk in chunks:
        score = cosine_similarity(query_embedding, chunk.embedding)
        scored.append((score, chunk))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [score for score in scored[:top_k]]
