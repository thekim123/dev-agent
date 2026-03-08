from dataclasses import dataclass, field


@dataclass
class DocumentChunk:
    chunk_id: str
    source_path: str
    text: str
    start: int
    end: int
    embedding: list[float] = field(default_factory=list)


def chunk_text(doc, chunk_size=1000, overlap=200):
    chunks = []
    start = 0
    text = doc["content"]
    while start < len(text):
        end = start + chunk_size
        chunk_id = doc["path"] + '_' + str(start) + '_' + str(end)
        chunk = DocumentChunk(chunk_id, doc['path'], text[start:end], start, end)
        chunks.append(chunk)
        start = end-overlap

        if end >= len(text):
            break
    return chunks


# documents 리스트 생성
# ↓
# chunk 분할
# ↓
# embedding 생성
# ↓
# vector search
# ↓
# LLM 답변
# if __name__ == "__main__":
#     project_root = 'D:/workspace/backend'
#     file_list = get_dir_list(project_root)
#     document_list = []
#     for doc in file_list:
#         document_list.append(chunk_text(doc))
#
#     load_dotenv()
#     embedded_chunks = []
#     bedrock = Embedder()
#
#     json_chunks = []
#     for document in document_list:
#         for chunk in document:
#             embedding = bedrock.embed(chunk.text)
#             chunk.embedding = embedding
#             json_chunks.append(asdict(chunk))
#
#     with open("vector_store.json", "w", encoding="utf-8") as f:
#         json.dump(json_chunks, f)


