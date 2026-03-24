def test_count_loads_chunks(opensearch_repo):
    # assert json_repo.count() == 3
    count = opensearch_repo.count()
    print(count)


def test_search_by_terms_returns_ranked_results(opensearch_repo):
    hits = opensearch_repo.search_by_term(["token", "refresh"])
    assert hits
    assert not any(hit.source_path.endswith(".md") for hit in hits)
