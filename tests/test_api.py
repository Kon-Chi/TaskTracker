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


def test_create_get_update_list_delete_task_flow() -> None:
    created = client.post(
        "/tasks",
        json={"title": "Write tests", "description": "Add API coverage"},
    )
    assert created.status_code == 201
    task = created.json()
    task_id = task["id"]
    assert task["title"] == "Write tests"
    assert task["is_completed"] is False

    fetched = client.get(f"/tasks/{task_id}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == task_id

    updated = client.patch(
        f"/tasks/{task_id}",
        json={"is_completed": True, "title": "Write API tests"},
    )
    assert updated.status_code == 200
    assert updated.json()["is_completed"] is True
    assert updated.json()["title"] == "Write API tests"

    listed = client.get("/tasks", params={"completed": True})
    assert listed.status_code == 200
    assert any(item["id"] == task_id for item in listed.json())

    deleted = client.delete(f"/tasks/{task_id}")
    assert deleted.status_code == 204

    missing = client.get(f"/tasks/{task_id}")
    assert missing.status_code == 404


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

    missing_patch = client.patch("/tasks/999999", json={"title": "x"})
    assert missing_patch.status_code == 404

    missing_delete = client.delete("/tasks/999999")
    assert missing_delete.status_code == 404

