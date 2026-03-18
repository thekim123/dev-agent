from pathlib import Path

from app.ingestion.opensearch_indexer import OpenSearchIndexer, load_chunks

if __name__ == "__main__":
    indexer = OpenSearchIndexer(host="http://localhost:9200", index_name="code_chunks", dimension=1024)

    indexer.client.delete(f"/code_chunks")
    # r = indexer.client.put(f"/code_chunks_demo", json=build_index_body(dimension=2)).raise_for_status()
    indexer.create_index()
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    VECTOR_STORE_PATH = BASE_DIR / 'vector_store.json'
    bulk_response = indexer.bulk_insert(load_chunks(VECTOR_STORE_PATH))
    print(bulk_response)
    # 문서 수 세기
