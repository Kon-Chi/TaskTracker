from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy import Select, or_, select
from sqlalchemy.orm import Session

from src.task_tracker.database import Base, engine, get_db
from src.task_tracker.models import Task
from src.task_tracker.schemas import TaskCreate, TaskResponse, TaskUpdate

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task Tracker API",
    description="Simple task tracking REST API for SQR quality-gates project.",
    version="0.1.0",
)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)) -> Task:
    task = Task(
        title=payload.title.strip(),
        description=payload.description.strip(),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@app.get("/tasks", response_model=list[TaskResponse])
def list_tasks(
    q: str | None = Query(default=None, description="Search in title/description"),
    completed: bool | None = Query(default=None, description="Filter by completion status"),
    db: Session = Depends(get_db),
) -> list[Task]:
    stmt: Select[tuple[Task]] = select(Task)
    if q:
        like_query = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(
                Task.title.ilike(like_query),
                Task.description.ilike(like_query),
            )
        )
    if completed is not None:
        stmt = stmt.where(Task.is_completed == completed)
    stmt = stmt.order_by(Task.created_at.desc())
    return db.execute(stmt).scalars().all()


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)) -> Task:
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@app.patch("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)) -> Task:
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    updates = payload.model_dump(exclude_unset=True)
    if "title" in updates and updates["title"] is not None:
        task.title = updates["title"].strip()
    if "description" in updates and updates["description"] is not None:
        task.description = updates["description"].strip()
    if "is_completed" in updates and updates["is_completed"] is not None:
        task.is_completed = updates["is_completed"]

    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)) -> None:
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    db.delete(task)
    db.commit()
    return None

