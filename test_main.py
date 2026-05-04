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
