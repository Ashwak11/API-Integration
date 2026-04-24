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

def test_get_syed():
    response = client.get("/ashwak/syed")
    assert response.status_code == 200
    assert response.text == "syed"

def test_ashwak_root_returns_404():
    response = client.get("/ashwak")
    assert response.status_code == 404

# --- Edge-case tests for /ashwak/syed (from analysis) ---

def test_get_syed_content_type_is_plain_text():
    """AC: response body is raw string 'syed', not JSON-quoted."""
    response = client.get("/ashwak/syed")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    # Must be raw text, not JSON-quoted string
    assert response.text == "syed"
    assert response.text != '"syed"'

def test_get_syed_trailing_slash_returns_404_or_200():
    """Edge-case: /ashwak/syed/ trailing slash should not 500."""
    response = client.get("/ashwak/syed/", follow_redirects=False)
    assert response.status_code in (200, 307, 308, 404)

def test_get_syed_post_method_not_allowed():
    """Edge-case: POST to /ashwak/syed should return 405 Method Not Allowed."""
    response = client.post("/ashwak/syed")
    assert response.status_code == 405

def test_get_syed_put_method_not_allowed():
    """Edge-case: PUT to /ashwak/syed should return 405 Method Not Allowed."""
    response = client.put("/ashwak/syed")
    assert response.status_code == 405

def test_get_syed_delete_method_not_allowed():
    """Edge-case: DELETE to /ashwak/syed should return 405 Method Not Allowed."""
    response = client.delete("/ashwak/syed")
    assert response.status_code == 405
