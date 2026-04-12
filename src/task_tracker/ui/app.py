import os
from typing import Any

import httpx
import streamlit as st

API_BASE_URL = os.getenv("TASK_TRACKER_API_URL", "http://127.0.0.1:8000")


def fetch_tasks(q: str = "", completed: str = "All") -> list[dict[str, Any]]:
    params: dict[str, Any] = {}
    if q.strip():
        params["q"] = q.strip()
    if completed == "Completed":
        params["completed"] = True
    elif completed == "Open":
        params["completed"] = False

    with httpx.Client(timeout=10.0) as client:
        response = client.get(f"{API_BASE_URL}/tasks", params=params)
        response.raise_for_status()
        return response.json()


def create_task(title: str, description: str) -> None:
    with httpx.Client(timeout=10.0) as client:
        response = client.post(
            f"{API_BASE_URL}/tasks",
            json={"title": title.strip(), "description": description.strip()},
        )
        response.raise_for_status()


def update_task(task_id: int, payload: dict[str, Any]) -> None:
    with httpx.Client(timeout=10.0) as client:
        response = client.patch(f"{API_BASE_URL}/tasks/{task_id}", json=payload)
        response.raise_for_status()


def delete_task(task_id: int) -> None:
    with httpx.Client(timeout=10.0) as client:
        response = client.delete(f"{API_BASE_URL}/tasks/{task_id}")
        response.raise_for_status()


def render_task(task: dict[str, Any]) -> None:
    with st.container(border=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"### {'✅' if task['is_completed'] else '⬜'} {task['title']}")
            if task["description"]:
                st.write(task["description"])
            st.caption(f"Task #{task['id']}")
        with col2:
            new_status = st.checkbox(
                "Completed",
                value=task["is_completed"],
                key=f"check_{task['id']}",
            )
            if new_status != task["is_completed"]:
                update_task(task["id"], {"is_completed": new_status})
                st.rerun()
            if st.button("Delete", key=f"delete_{task['id']}"):
                delete_task(task["id"])
                st.rerun()


def main() -> None:
    st.set_page_config(page_title="Task Tracker", page_icon="🧾", layout="centered")
    st.title("Task Tracker")
    st.caption("Simple Streamlit UI backed by FastAPI + SQLite")

    with st.form("create_task_form", clear_on_submit=True):
        title = st.text_input("Title", max_chars=120)
        description = st.text_area("Description", max_chars=2000)
        submitted = st.form_submit_button("Create task")
        if submitted:
            if not title.strip():
                st.error("Title cannot be empty.")
            else:
                create_task(title, description)
                st.success("Task created.")
                st.rerun()

    search = st.text_input("Search tasks")
    status_filter = st.selectbox("Status", options=["All", "Open", "Completed"])
    st.divider()

    try:
        tasks = fetch_tasks(q=search, completed=status_filter)
        if not tasks:
            st.info("No tasks found.")
        for task in tasks:
            render_task(task)
    except httpx.HTTPError as exc:
        st.error(f"Failed to communicate with API: {exc}")


if __name__ == "__main__":
    main()

