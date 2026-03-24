def test_count_loads_chunks(json_repo):
    assert json_repo.count() == 3


def test_search_similar_returns_top_k_sorted(json_repo):
    hits = json_repo.search_similar([1.0, 0.0], top_k=1)
    assert len(hits) == 1
    hit = hits[0]
    assert hit.chunk_id == "a"


def test_search_by_terms_returns_ranked_results(json_repo):
    hits = json_repo.search_by_term(["token", "refresh"])
    assert hits
    assert hits[0].source_path == "app/auth/token_service.py"
    assert not any(hit.source_path.endswith(".md") for hit in hits)
