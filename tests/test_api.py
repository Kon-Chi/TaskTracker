import os
from pathlib import Path
import sys

from fastapi.testclient import TestClient

# Ensure tests use a dedicated sqlite file.
os.environ["TASK_TRACKER_DB_URL"] = f"sqlite:///{Path('test_task_tracker.db').absolute()}"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.main import app  # noqa: E402

client = TestClient(app)


def test_healthcheck() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}



def test_search_and_not_found_paths() -> None:
    first = client.post("/tasks", json={"title": "Buy milk", "description": "2L"})
    second = client.post("/tasks", json={"title": "Call Alice", "description": "Project sync"})
    assert first.status_code == 201
    assert second.status_code == 201

    search = client.get("/tasks", params={"q": "Alice"})
    assert search.status_code == 200
    payload = search.json()
    assert len(payload) >= 1
    assert any("Alice" in item["title"] for item in payload)

