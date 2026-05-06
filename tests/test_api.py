def test_home(client):
    res = client.get("/")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "healthy"


def test_get_transactions_without_token(client):
    res = client.get("/get_transactions")
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_etl_run(client):
    res = client.post("/etl/run", json={"source": "data/sample_transactions.csv"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert body["rows_loaded"] > 0


def test_list_stored_transactions(client):
    client.post("/etl/run", json={"source": "data/sample_transactions.csv"})
    res = client.get("/transactions?limit=10")
    assert res.status_code == 200
    body = res.get_json()
    assert "transactions" in body
    assert body["count"] <= 10
