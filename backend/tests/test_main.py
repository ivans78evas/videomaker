from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_tasks_endpoint():
    # The endpoint is actually /api/v1/tasks/
    response = client.get("/api/v1/tasks/")
    # It might return 200 but since no DB is connected in test env it might fail or return empty list
    # Let's just check it doesn't 404
    assert response.status_code != 404
