import json
import os

import numpy as np

from chunker import DocumentChunk
from embedder import Embedder

ALLOWED = (".java", ".md", ".yml", ".txt", ".properties")
EXCLUDED_DIRS = {".gradle", "gradle", ".github", "build", "target", ".git", ".idea", "node_modules", "__pycache__"}

bedrock = Embedder()


# loader.load_vector_store, loader.search_chunks를 감싸서
# retrieve_docs(question)를 만들고,
# 반환값에 chunk_id/source_path/start/end/score를 붙여줘.
def retrieve_docs(question):
    vectors = load_vector_store("vector_store.json")
    query_embed = bedrock.embed(question)
    search_list = search_chunks(query_embed, vectors)
    return search_list
    # if search_list[0][0] < 0.5:
    #     print('지금 가지고 있는 자료에서는 마땅한 데이터가 없네요.... 잘 모르겠어요....')
    # else:
    #     doc_text = ''
    #     for doc in search_list:
    #         doc_text += doc[1].text
    #     query_result = bedrock.query_embed(doc_text, query)
    #     print(query_result)
    #     print('참고파일: ')
    #     for i, (_, search) in enumerate(search_list):
    #         print(f'{i}: {search.source_path}')
    #
    # return None


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
    with open(path, "r", encoding="utf-8") as f:
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


if __name__ == "__main__":
    chunk_list = load_vector_store()
    bedrock = Embedder()
    query = '인증 모듈의 역할은 무엇인가?'
    query = '이 프로젝트에서 SAML 인증 흐름이 어떻게 돼?'
    query_embed = bedrock.embed(query)
    search_list = search_chunks(query_embed, chunk_list)
    if search_list[0][0] < 0.5:
        print('지금 가지고 있는 자료에서는 마땅한 데이터가 없네요.... 잘 모르겠어요....')
    else:
        doc_text = ''
        for doc in search_list:
            doc_text += doc[1].text
        query_result = bedrock.query_embed(doc_text, query)
        print(query_result)
        print('참고파일: ')
        for i, (_, search) in enumerate(search_list):
            print(f'{i}: {search.source_path}')
