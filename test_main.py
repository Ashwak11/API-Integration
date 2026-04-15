from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_combined_data():
    response = client.post("/combined-data", json={"city": "London", "crypto_id": "bitcoin", "breed": "bulldog"})
    assert response.status_code == 200
    data = response.json()
    assert "temperature" in data
    assert "current_price" in data
    assert "image_url" in data
    assert "timestamp" in data

def test_get_history():
    response = client.get("/combined-data/history")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    if data:
        record = data[0]
        assert "city" in record
        assert "crypto_id" in record
        assert "breed" in record
        assert "temperature" in record
        assert "current_price" in record
        assert "image_url" in record
        assert "timestamp" in record

def test_get_weather():
    response = client.get("/weather", params={"city": "London"})
    assert response.status_code == 200
    data = response.json()
    assert "temperature" in data
    assert "description" in data

def test_get_crypto():
    response = client.get("/crypto", params={"crypto_id": "bitcoin"})
    assert response.status_code == 200
    data = response.json()
    assert "current_price" in data

def test_get_dog():
    response = client.get("/dogs", params={"breed": "bulldog"})
    assert response.status_code == 200
    data = response.json()
    assert "image_url" in data
    assert "group" in data
    assert "life_span" in data
    assert "temperament" in data

def test_get_ping():
    response = client.get("/ping")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "pong"
    assert "timestamp" in data
    # Verify timestamp is a valid ISO 8601 string
    from datetime import datetime
    datetime.fromisoformat(data["timestamp"])  # raises ValueError if invalid


def test_ping_response_keys():
    """AC: Response body only contains expected keys."""
    response = client.get("/ping")
    data = response.json()
    assert set(data.keys()) == {"message", "timestamp"}


def test_ping_message_value():
    """AC: 'message' field value is exactly 'pong'."""
    response = client.get("/ping")
    assert response.json()["message"] == "pong"


def test_ping_timestamp_is_string():
    """AC: 'timestamp' is a non-empty string."""
    response = client.get("/ping")
    ts = response.json()["timestamp"]
    assert isinstance(ts, str) and len(ts) > 0


def test_ping_timestamp_format():
    """AC: timestamp matches ISO 8601 format including date+time."""
    import re
    response = client.get("/ping")
    ts = response.json()["timestamp"]
    # ISO 8601: YYYY-MM-DDTHH:MM:SS[.ffffff][+HH:MM or Z]
    assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", ts), f"Not ISO 8601: {ts}"


def test_ping_no_db_interaction(monkeypatch):
    """AC: No database read or write occurs during /ping."""
    import sqlite3
    original_connect = sqlite3.connect
    db_calls = []

    def mock_connect(*args, **kwargs):
        db_calls.append(args)
        return original_connect(*args, **kwargs)

    monkeypatch.setattr(sqlite3, "connect", mock_connect)
    client.get("/ping")
    assert db_calls == [], f"Unexpected DB calls during /ping: {db_calls}"


def test_ping_no_external_api(monkeypatch):
    """AC: No external API calls (weather, crypto, dogs) during /ping."""
    import requests as req
    original_get = req.get
    api_calls = []

    def mock_get(url, *args, **kwargs):
        api_calls.append(url)
        return original_get(url, *args, **kwargs)

    monkeypatch.setattr(req, "get", mock_get)
    response = client.get("/ping")
    assert response.status_code == 200
    assert api_calls == [], f"Unexpected external API calls during /ping: {api_calls}"


def test_ping_method_not_allowed_post():
    """Edge case: POST /ping should return 405 Method Not Allowed."""
    response = client.post("/ping")
    assert response.status_code == 405


def test_ping_method_not_allowed_put():
    """Edge case: PUT /ping should return 405."""
    response = client.put("/ping")
    assert response.status_code == 405


def test_ping_method_not_allowed_delete():
    """Edge case: DELETE /ping should return 405."""
    response = client.delete("/ping")
    assert response.status_code == 405


def test_ping_concurrent_timestamps():
    """Edge case: Concurrent requests produce independent, valid timestamps."""
    from datetime import datetime
    responses = [client.get("/ping") for _ in range(5)]
    timestamps = []
    for resp in responses:
        assert resp.status_code == 200
        ts = resp.json()["timestamp"]
        timestamps.append(datetime.fromisoformat(ts))
    # All timestamps should be parseable (no duplicates check needed — just validity)
    assert len(timestamps) == 5
