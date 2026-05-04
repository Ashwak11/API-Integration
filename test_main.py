from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
import pytest
from fastapi import HTTPException
from main import app, fetch_weather_data, fetch_crypto_data, fetch_dog_data

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

def test_zingzong():
    """AC1 & AC2: GET /zing/zong returns 200 with 'zong' in body."""
    response = client.get("/zing/zong")
    assert response.status_code == 200
    assert "zong" in response.text


def test_zingzong_response_body():
    """AC2: Response body contains the string 'zong' in the JSON message field."""
    response = client.get("/zing/zong")
    data = response.json()
    assert "message" in data
    assert data["message"] == "zong"


def test_zingzong_content_type():
    """AC3: Endpoint returns JSON content-type."""
    response = client.get("/zing/zong")
    assert "application/json" in response.headers["content-type"]


def test_zingzong_no_params_required():
    """AC3: Endpoint is reachable with no query params or body."""
    response = client.get("/zing/zong")
    assert response.status_code == 200


def test_zingzong_post_method_not_allowed():
    """Edge case: POST to /zing/zong should return 405 Method Not Allowed."""
    response = client.post("/zing/zong")
    assert response.status_code == 405


def test_zingzong_put_method_not_allowed():
    """Edge case: PUT to /zing/zong should return 405 Method Not Allowed."""
    response = client.put("/zing/zong")
    assert response.status_code == 405


def test_zingzong_delete_method_not_allowed():
    """Edge case: DELETE to /zing/zong should return 405 Method Not Allowed."""
    response = client.delete("/zing/zong")
    assert response.status_code == 405


def test_zingzong_ignores_extra_query_params():
    """Edge case: Extra query params are gracefully ignored."""
    response = client.get("/zing/zong", params={"foo": "bar"})
    assert response.status_code == 200
    assert "zong" in response.text


def test_existing_history_endpoint_unaffected():
    """AC4: Existing /combined-data/history endpoint is unaffected."""
    response = client.get("/combined-data/history")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_existing_weather_endpoint_unaffected():
    """AC4: Existing /weather endpoint still registered (returns 422 when missing param, not 404)."""
    response = client.get("/weather")
    assert response.status_code == 422  # missing required 'city' param, not 404


def test_existing_crypto_endpoint_unaffected():
    """AC4: Existing /crypto endpoint still registered."""
    response = client.get("/crypto")
    assert response.status_code == 422  # missing required 'crypto_id' param


def test_existing_dogs_endpoint_unaffected():
    """AC4: Existing /dogs endpoint still registered."""
    response = client.get("/dogs")
    assert response.status_code == 422  # missing required 'breed' param

# ── Mock-based unit tests for external API functions ──────────────────────────

def _mock_weather_response():
    mock = MagicMock()
    mock.raise_for_status = MagicMock()
    mock.json.return_value = {
        "main": {"temp": 15.0},
        "weather": [{"description": "clear sky"}]
    }
    return mock

def _mock_crypto_response():
    mock = MagicMock()
    mock.raise_for_status = MagicMock()
    mock.json.return_value = {"bitcoin": {"usd": 60000.0}}
    return mock

def _mock_breeds_response():
    mock = MagicMock()
    mock.raise_for_status = MagicMock()
    mock.json.return_value = [{"id": 1, "name": "Bulldog", "breed_group": "Non-Sporting", "life_span": "8-10 years", "temperament": "Friendly"}]
    return mock

def _mock_dog_image_response():
    mock = MagicMock()
    mock.raise_for_status = MagicMock()
    mock.json.return_value = [{"url": "https://example.com/bulldog.jpg"}]
    return mock


class TestFetchWeatherData:
    @patch("main.requests.get")
    def test_success(self, mock_get):
        mock_get.return_value = _mock_weather_response()
        result = fetch_weather_data("London")
        assert result["temperature"] == 15.0
        assert result["description"] == "clear sky"

    @patch("main.requests.get")
    def test_http_error(self, mock_get):
        import requests as req
        mock = MagicMock()
        mock.raise_for_status.side_effect = req.exceptions.HTTPError("bad")
        mock_get.return_value = mock
        with pytest.raises(HTTPException) as exc_info:
            fetch_weather_data("Unknown")
        assert exc_info.value.status_code == 400

    @patch("main.requests.get")
    def test_unexpected_error(self, mock_get):
        mock_get.side_effect = Exception("network failure")
        with pytest.raises(HTTPException) as exc_info:
            fetch_weather_data("London")
        assert exc_info.value.status_code == 500


class TestFetchCryptoData:
    @patch("main.requests.get")
    def test_success(self, mock_get):
        mock_get.return_value = _mock_crypto_response()
        result = fetch_crypto_data("bitcoin")
        assert result["current_price"] == 60000.0

    @patch("main.requests.get")
    def test_http_error(self, mock_get):
        import requests as req
        mock = MagicMock()
        mock.raise_for_status.side_effect = req.exceptions.HTTPError("bad")
        mock_get.return_value = mock
        with pytest.raises(HTTPException) as exc_info:
            fetch_crypto_data("unknown-coin")
        assert exc_info.value.status_code == 400

    @patch("main.requests.get")
    def test_unexpected_error(self, mock_get):
        mock_get.side_effect = Exception("timeout")
        with pytest.raises(HTTPException) as exc_info:
            fetch_crypto_data("bitcoin")
        assert exc_info.value.status_code == 500


class TestFetchDogData:
    @patch("main.requests.get")
    def test_success(self, mock_get):
        mock_get.side_effect = [_mock_breeds_response(), _mock_dog_image_response()]
        result = fetch_dog_data("bulldog")
        assert result["image_url"] == "https://example.com/bulldog.jpg"
        assert result["group"] == "Non-Sporting"

    @patch("main.requests.get")
    def test_breed_not_found(self, mock_get):
        mock = MagicMock()
        mock.json.return_value = []
        mock_get.return_value = mock
        with pytest.raises(HTTPException) as exc_info:
            fetch_dog_data("unicorn")
        assert exc_info.value.status_code == 404


class TestGetWeatherEndpoint:
    @patch("main.fetch_weather_data")
    def test_success(self, mock_fn):
        mock_fn.return_value = {"temperature": 20.0, "description": "sunny"}
        response = client.get("/weather", params={"city": "Paris"})
        assert response.status_code == 200
        assert response.json()["temperature"] == 20.0


class TestGetCryptoEndpoint:
    @patch("main.fetch_crypto_data")
    def test_success(self, mock_fn):
        mock_fn.return_value = {"current_price": 50000.0}
        response = client.get("/crypto", params={"crypto_id": "bitcoin"})
        assert response.status_code == 200
        assert response.json()["current_price"] == 50000.0


class TestGetDogEndpoint:
    @patch("main.fetch_dog_data")
    def test_success(self, mock_fn):
        mock_fn.return_value = {
            "image_url": "https://example.com/dog.jpg",
            "group": "Sporting",
            "life_span": "10-12 years",
            "temperament": "Friendly"
        }
        response = client.get("/dogs", params={"breed": "labrador"})
        assert response.status_code == 200
        assert "image_url" in response.json()


class TestGetCombinedDataEndpoint:
    @patch("main.fetch_dog_data")
    @patch("main.fetch_crypto_data")
    @patch("main.fetch_weather_data")
    def test_success(self, mock_weather, mock_crypto, mock_dog):
        mock_weather.return_value = {"temperature": 10.0, "description": "cloudy"}
        mock_crypto.return_value = {"current_price": 3000.0}
        mock_dog.return_value = {
            "image_url": "https://example.com/dog.jpg",
            "group": "Herding",
            "life_span": "12-14 years",
            "temperament": "Active"
        }
        response = client.post(
            "/combined-data",
            params={"city": "Berlin", "crypto_id": "ethereum", "breed": "collie"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["city"] == "Berlin"
        assert data["temperature"] == 10.0
        assert data["current_price"] == 3000.0
        assert "timestamp" in data


class TestGetHistoryDateFilter:
    def test_with_date_range(self):
        response = client.get(
            "/combined-data/history",
            params={"start_date": "2000-01-01T00:00:00", "end_date": "2000-01-02T00:00:00"}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)


import subprocess
import sys

def test_startup_message():
    result = subprocess.run(
        [sys.executable, "main.py"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"
    assert "Hello from my test story!" in result.stdout, (
        f"Expected message not found in stdout: {result.stdout!r}"
    )
