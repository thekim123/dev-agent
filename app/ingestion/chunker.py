from app.ingestion.models import DocumentChunk


def chunk_text(doc, chunk_size=1000, overlap=200):
    chunks = []
    start = 0
    text = doc["content"]
    while start < len(text):
        end = start + chunk_size
        chunk_id = doc["path"] + '_' + str(start) + '_' + str(end)
        chunk = DocumentChunk(chunk_id, doc['path'], text[start:end], start, end)
        chunks.append(chunk)
        start = end - overlap

        if end >= len(text):
            break
    return chunks
