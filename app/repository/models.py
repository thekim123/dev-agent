from dataclasses import dataclass


@dataclass(frozen=True)
class ChunkSearchHit:
    chunk_id: str
    source_path: str
    text: str
    start: int
    end: int
    score: float
