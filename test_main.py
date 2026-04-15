from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime
from main import app

client = TestClient(app)

# ---------------------------------------------------------------------------
# Helper mock data
# ---------------------------------------------------------------------------
MOCK_WEATHER_RESP = MagicMock(status_code=200)
MOCK_WEATHER_RESP.raise_for_status = MagicMock()
MOCK_WEATHER_RESP.json.return_value = {
    "main": {"temp": 15.0},
    "weather": [{"description": "clear sky"}],
}

MOCK_CRYPTO_RESP = MagicMock(status_code=200)
MOCK_CRYPTO_RESP.raise_for_status = MagicMock()
MOCK_CRYPTO_RESP.json.return_value = {"bitcoin": {"usd": 50000.0}}

MOCK_BREEDS_RESP = MagicMock(status_code=200)
MOCK_BREEDS_RESP.raise_for_status = MagicMock()
MOCK_BREEDS_RESP.json.return_value = [
    {"id": 1, "name": "Bulldog", "breed_group": "Non-Sporting", "life_span": "8-10 years", "temperament": "Docile"}
]

MOCK_IMAGE_RESP = MagicMock(status_code=200)
MOCK_IMAGE_RESP.raise_for_status = MagicMock()
MOCK_IMAGE_RESP.json.return_value = [{"url": "https://example.com/dog.jpg"}]


def _make_requests_get_side_effect(url, **kwargs):
    """Route mock requests to the right mock response based on URL."""
    if "openweathermap" in url:
        return MOCK_WEATHER_RESP
    if "coingecko" in url:
        return MOCK_CRYPTO_RESP
    if "breeds" in url:
        return MOCK_BREEDS_RESP
    if "images/search" in url:
        return MOCK_IMAGE_RESP
    raise ValueError(f"Unexpected URL in test: {url}")


# ---------------------------------------------------------------------------
# Combined-data tests (mocked external APIs + DB)
# ---------------------------------------------------------------------------

@patch("main.requests.get", side_effect=_make_requests_get_side_effect)
@patch("main.sqlite3.connect")
def test_get_combined_data(mock_connect, mock_get):
    mock_cursor = MagicMock()
    mock_connect.return_value.__enter__ = MagicMock(return_value=mock_connect.return_value)
    mock_connect.return_value.cursor.return_value = mock_cursor

    response = client.post("/combined-data", params={"city": "London", "crypto_id": "bitcoin", "breed": "bulldog"})
    assert response.status_code == 200
    data = response.json()
    assert "temperature" in data
    assert "current_price" in data
    assert "image_url" in data
    assert "timestamp" in data


@patch("main.sqlite3.connect")
def test_get_history(mock_connect):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        (1, "London", "bitcoin", "bulldog", 15.0, 50000.0, "https://example.com/dog.jpg", "2026-04-14T10:00:00")
    ]
    mock_connect.return_value.cursor.return_value = mock_cursor

    response = client.get("/combined-data/history")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    record = data[0]
    for field in ("city", "crypto_id", "breed", "temperature", "current_price", "image_url", "timestamp"):
        assert field in record


@patch("main.sqlite3.connect")
def test_get_history_with_date_filter(mock_connect):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = []
    mock_connect.return_value.cursor.return_value = mock_cursor

    response = client.get("/combined-data/history", params={"start_date": "2026-01-01", "end_date": "2026-12-31"})
    assert response.status_code == 200
    assert response.json() == []


# ---------------------------------------------------------------------------
# Individual endpoint tests (mocked)
# ---------------------------------------------------------------------------

@patch("main.requests.get", return_value=MOCK_WEATHER_RESP)
def test_get_weather(mock_get):
    response = client.get("/weather", params={"city": "London"})
    assert response.status_code == 200
    data = response.json()
    assert "temperature" in data
    assert "description" in data


@patch("main.requests.get", return_value=MOCK_CRYPTO_RESP)
def test_get_crypto(mock_get):
    response = client.get("/crypto", params={"crypto_id": "bitcoin"})
    assert response.status_code == 200
    data = response.json()
    assert "current_price" in data


@patch("main.requests.get", side_effect=_make_requests_get_side_effect)
def test_get_dog(mock_get):
    response = client.get("/dogs", params={"breed": "bulldog"})
    assert response.status_code == 200
    data = response.json()
    assert "image_url" in data
    assert "group" in data
    assert "life_span" in data
    assert "temperament" in data


@patch("main.requests.get", side_effect=_make_requests_get_side_effect)
def test_get_dog_not_found(mock_get):
    response = client.get("/dogs", params={"breed": "unknown_breed_xyz"})
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Error-handling paths
# ---------------------------------------------------------------------------

@patch("main.requests.get")
def test_fetch_weather_http_error(mock_get):
    import requests as req
    mock_resp = MagicMock()
    mock_resp.raise_for_status.side_effect = req.exceptions.HTTPError("bad request")
    mock_get.return_value = mock_resp
    response = client.get("/weather", params={"city": "NoCity"})
    assert response.status_code == 400


@patch("main.requests.get")
def test_fetch_weather_unexpected_error(mock_get):
    mock_get.side_effect = Exception("network failure")
    response = client.get("/weather", params={"city": "NoCity"})
    assert response.status_code == 500


@patch("main.requests.get")
def test_fetch_crypto_http_error(mock_get):
    import requests as req
    mock_resp = MagicMock()
    mock_resp.raise_for_status.side_effect = req.exceptions.HTTPError("bad request")
    mock_get.return_value = mock_resp
    response = client.get("/crypto", params={"crypto_id": "badcoin"})
    assert response.status_code == 400


@patch("main.requests.get")
def test_fetch_crypto_unexpected_error(mock_get):
    mock_get.side_effect = Exception("network failure")
    response = client.get("/crypto", params={"crypto_id": "badcoin"})
    assert response.status_code == 500


# ---------------------------------------------------------------------------
# Health check endpoint tests (AC verification)
# ---------------------------------------------------------------------------

def test_get_health():
    """AC1: GET /health returns HTTP 200 OK"""
    response = client.get("/health")
    assert response.status_code == 200


def test_get_health_status_ok():
    """AC2: Response includes 'status' field with value 'ok'"""
    response = client.get("/health")
    data = response.json()
    assert data["status"] == "ok"


def test_get_health_timestamp_present_and_valid_iso():
    """AC3: Response includes 'timestamp' in ISO 8601 format"""
    response = client.get("/health")
    data = response.json()
    assert "timestamp" in data
    datetime.fromisoformat(data["timestamp"])  # raises ValueError if invalid


def test_get_health_content_type():
    """Edge case: Content-Type must be application/json"""
    response = client.get("/health")
    assert "application/json" in response.headers["content-type"]


def test_get_health_no_external_api_calls():
    """AC4: The endpoint must not call any external APIs"""
    with patch("main.requests.get") as mock_get:
        response = client.get("/health")
        assert response.status_code == 200
        mock_get.assert_not_called()


def test_get_health_no_database_interaction():
    """AC5: The endpoint must not interact with the database"""
    with patch("main.sqlite3.connect") as mock_connect:
        response = client.get("/health")
        assert response.status_code == 200
        mock_connect.assert_not_called()


def test_get_health_timestamp_is_dynamic():
    """Edge case: Timestamp must reflect actual current time, not a cached value"""
    import time
    response1 = client.get("/health")
    time.sleep(0.01)
    response2 = client.get("/health")
    ts1 = response1.json()["timestamp"]
    ts2 = response2.json()["timestamp"]
    # Both are valid ISO strings and represent independent points in time
    datetime.fromisoformat(ts1)
    datetime.fromisoformat(ts2)
    # Timestamps should be different (dynamic per-request)
    assert ts1 != ts2
