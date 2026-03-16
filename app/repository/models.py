from dataclasses import dataclass


@dataclass(frozen=True)
class ChunkSearchHit:
    chunk_id: str
    source_path: str
    text: str
    start_offset: int
    end_offset: int
    score: float
