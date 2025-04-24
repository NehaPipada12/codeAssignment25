import io
import json
import pytest
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Upload your CSV file" in response.data

def test_valid_upload(client):
    csv_content = b"""Date,Description,Amount
2024-04-01,Amazon Purchase,200
2024-04-02,Pizza Hut,150
2024-04-03,Uber,100
"""
    with open("categories.json", "w") as f:
        json.dump({
            "Shopping": ["amazon"],
            "Dining": ["pizza"],
            "Transport": ["uber"]
        }, f)

    data = {
        "file": (io.BytesIO(csv_content), "test.csv")
    }
    response = client.post("/upload", data=data, content_type="multipart/form-data")
    assert response.status_code == 200

    json_data = response.get_json()
    assert "labels" in json_data
    assert "values" in json_data
    assert "Shopping" in json_data["labels"]
    assert "Dining" in json_data["labels"]
    assert "Transport" in json_data["labels"]

def test_upload_missing_columns(client):
    csv_content = b"""Date,Text,Amount
2024-04-01,Uber ride,100
"""
    data = {
        "file": (io.BytesIO(csv_content), "bad.csv")
    }
    response = client.post("/upload", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    assert b"CSV must include Date, Description, and Amount" in response.data

def test_no_file_provided(client):
    response = client.post("/upload", data={}, content_type="multipart/form-data")
    assert response.status_code == 400
    json_data = response.get_json()
    assert "error" in json_data
    assert json_data["error"] == "No file provided"

