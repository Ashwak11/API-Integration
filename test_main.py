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

def test_get_fingfong():
    response = client.get("/fingfong")
    assert response.status_code == 200
    assert response.text == "fong"

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
