from dataclasses import dataclass, field


@dataclass
class DocumentChunk:
    chunk_id: str
    source_path: str
    text: str
    start: int
    end: int
    embedding: list[float] = field(default_factory=list)
