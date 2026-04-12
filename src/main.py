from fastapi import FastAPI

app = FastAPI(
    title="Task Tracker API",
    description="Simple task tracking REST API for SQR quality-gates project.",
    version="0.1.0",
)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}

