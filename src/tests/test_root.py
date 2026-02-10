# src/tests/test_root.py
def test_root(client):
    res = client.get("/")
    assert res.json().get("message") == "welcome to my api"
    assert res.status_code == 200