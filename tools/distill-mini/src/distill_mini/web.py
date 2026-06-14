"""FastAPI application for the local distillation pipeline workbench."""

from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from distill_mini.clients.openai_client import MissingOpenAIKeyError
from distill_mini.service import DistillService


STATIC_DIR = Path(__file__).parent / "static"
service = DistillService()
app = FastAPI(title="PersonOS Distill Mini", docs_url="/api/docs")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class QuestionRequest(BaseModel):
    """Payload for creating a new test question."""

    question: str


class TeacherRequest(BaseModel):
    """Payload for saving a manual teacher answer."""

    output: str


class BatchRequest(BaseModel):
    """Optional selected input IDs; an empty list means all pending items."""

    input_ids: list[str] = Field(default_factory=list)


@app.get("/")
def index() -> FileResponse:
    """Serve the single-page local workbench."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/snapshot")
def snapshot() -> dict:
    """Return the complete current pipeline snapshot."""
    return service.snapshot()


@app.post("/api/inputs")
def add_input(request: QuestionRequest) -> dict:
    """Create one input question."""
    try:
        return service.add_input(request.question).model_dump(mode="json")
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.put("/api/inputs/{input_id}/teacher")
def save_teacher(input_id: str, request: TeacherRequest) -> dict:
    """Save or revise one manual teacher answer."""
    try:
        return service.save_teacher(input_id, request.output).model_dump(mode="json")
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/api/batch/student")
def collect_student(request: BatchRequest) -> dict:
    """Generate student answers for selected or all pending inputs."""
    try:
        count = service.collect_students(request.input_ids)
        return {"processed": count}
    except (MissingOpenAIKeyError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/api/batch/compare")
def compare(request: BatchRequest) -> dict:
    """Judge selected or all pending teacher/student pairs."""
    try:
        count = service.compare(request.input_ids)
        return {"processed": count}
    except (MissingOpenAIKeyError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/api/export-sft")
def export_sft() -> FileResponse:
    """Build and download the current SFT dataset."""
    destination, _ = service.export_sft()
    return FileResponse(
        destination,
        media_type="application/x-ndjson",
        filename="dataset_sft.jsonl",
    )


def run() -> None:
    """Start the local web client."""
    uvicorn.run("distill_mini.web:app", host="127.0.0.1", port=8765, reload=False)
