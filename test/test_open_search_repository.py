def test_count_loads_chunks(opensearch_repo):
    # assert json_repo.count() == 3
    count = opensearch_repo.count()
    print(count)
