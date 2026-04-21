# test_api.py
import pytest
import requests

BASE_URL = "http://localhost:8000"  # Replace with your API base URL

def test_get_items():
    payload = {
  "additionalProp1": {"repo_path":"//github.com/roopendrasalvi/code_pipeline"}
}
    response = requests.post(f"{BASE_URL}/index", json = payload)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    # assert "id" in data[0]

# def test_create_item():
#     payload = {"name": "Test Item", "price": 99.99}
#     response = requests.post(f"{BASE_URL}/items", json=payload)
#     assert response.status_code == 201
#     data = response.json()
#     assert data["name"] == "Test Item"
#     assert data["price"] == 99.99

# def test_invalid_item():
#     payload = {"name": "", "price": -10}
#     response = requests.post(f"{BASE_URL}/items", json=payload)
#     assert response.status_code == 400
