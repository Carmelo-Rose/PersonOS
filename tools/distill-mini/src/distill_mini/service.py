"""Shared application service used by both the CLI and local web client."""

from pathlib import Path
from threading import Lock
from uuid import uuid4

from distill_mini.clients.openai_client import OpenAIClient
from distill_mini.config import DATA_DIR, load_settings
from distill_mini.models import ComparisonRecord, InputRecord, OutputRecord
from distill_mini.prompts import STUDENT_SYSTEM_PROMPT
from distill_mini.storage import JsonlRepository, write_jsonl


class DistillService:
    """Coordinate local JSONL records and model-backed batch operations."""

    def __init__(self, data_dir: Path = DATA_DIR) -> None:
        self.data_dir = data_dir
        self.inputs = JsonlRepository(data_dir / "inputs.jsonl", InputRecord)
        self.teacher_outputs = JsonlRepository(
            data_dir / "teacher_outputs.jsonl", OutputRecord
        )
        self.student_outputs = JsonlRepository(
            data_dir / "student_outputs.jsonl", OutputRecord
        )
        self.comparisons = JsonlRepository(
            data_dir / "comparisons.jsonl", ComparisonRecord
        )
        self._write_lock = Lock()

    @staticmethod
    def _latest(records: list) -> dict[str, object]:
        """Index append-only records by input ID, keeping the latest value."""
        return {record.input_id: record for record in records}

    def snapshot(self) -> dict:
        """Return all questions enriched with their current pipeline state."""
        teachers = self._latest(self.teacher_outputs.read_all())
        students = self._latest(self.student_outputs.read_all())
        comparisons = self._latest(self.comparisons.read_all())
        items = []

        for input_record in reversed(self.inputs.read_all()):
            teacher = teachers.get(input_record.id)
            student = students.get(input_record.id)
            comparison = comparisons.get(input_record.id)
            if comparison:
                stage = "judged"
            elif student:
                stage = "student"
            elif teacher:
                stage = "teacher"
            else:
                stage = "inputs"
            items.append(
                {
                    "input": input_record.model_dump(mode="json"),
                    "teacher": teacher.model_dump(mode="json") if teacher else None,
                    "student": student.model_dump(mode="json") if student else None,
                    "comparison": (
                        comparison.model_dump(mode="json") if comparison else None
                    ),
                    "stage": stage,
                }
            )

        settings = load_settings()
        return {
            "items": items,
            "counts": {
                stage: sum(item["stage"] == stage for item in items)
                for stage in ("inputs", "teacher", "student", "judged")
            },
            "openai_connected": bool(settings.openai_api_key),
            "student_model": settings.student_model,
            "judge_model": settings.judge_model,
        }

    def add_input(self, question: str) -> InputRecord:
        """Add a non-empty test question."""
        cleaned = question.strip()
        if not cleaned:
            raise ValueError("Question cannot be empty.")
        record = InputRecord(id=uuid4().hex, question=cleaned)
        with self._write_lock:
            self.inputs.append(record)
        return record

    def save_teacher(self, input_id: str, output: str) -> OutputRecord:
        """Append a manual teacher answer for one input."""
        cleaned = output.strip()
        if not cleaned:
            raise ValueError("Teacher answer cannot be empty.")
        if input_id not in {record.id for record in self.inputs.read_all()}:
            raise ValueError("Input not found.")
        record = OutputRecord(
            input_id=input_id, output=cleaned, source="teacher", model="manual"
        )
        with self._write_lock:
            self.teacher_outputs.append(record)
        return record

    def collect_students(self, input_ids: list[str] | None = None) -> int:
        """Generate student outputs for selected or all pending inputs."""
        settings = load_settings()
        client = OpenAIClient(settings.openai_api_key, settings.openai_base_url)
        teachers = self._latest(self.teacher_outputs.read_all())
        existing = self._latest(self.student_outputs.read_all())
        selected = set(input_ids or [])
        pending = [
            record
            for record in self.inputs.read_all()
            if record.id in teachers
            and record.id not in existing
            and (not selected or record.id in selected)
        ]
        for input_record in pending:
            answer = client.generate(
                settings.student_model, STUDENT_SYSTEM_PROMPT, input_record.question
            )
            with self._write_lock:
                self.student_outputs.append(
                    OutputRecord(
                        input_id=input_record.id,
                        output=answer,
                        source="student",
                        model=settings.student_model,
                    )
                )
        return len(pending)

    def compare(self, input_ids: list[str] | None = None) -> int:
        """Judge selected or all pending teacher/student pairs."""
        settings = load_settings()
        client = OpenAIClient(settings.openai_api_key, settings.openai_base_url)
        teachers = self._latest(self.teacher_outputs.read_all())
        students = self._latest(self.student_outputs.read_all())
        compared = self._latest(self.comparisons.read_all())
        selected = set(input_ids or [])
        pending = [
            record
            for record in self.inputs.read_all()
            if record.id in teachers
            and record.id in students
            and record.id not in compared
            and (not selected or record.id in selected)
        ]
        for input_record in pending:
            result = client.judge(
                settings.judge_model,
                input_record.question,
                teachers[input_record.id].output,
                students[input_record.id].output,
            )
            with self._write_lock:
                self.comparisons.append(
                    ComparisonRecord(
                        input_id=input_record.id,
                        winner=result.winner,
                        score=result.score,
                        reason=result.reason,
                        judge_model=settings.judge_model,
                    )
                )
        return len(pending)

    def export_sft(self) -> tuple[Path, int]:
        """Rebuild the chat-format SFT dataset from latest teacher answers."""
        teachers = self._latest(self.teacher_outputs.read_all())
        dataset = [
            {
                "messages": [
                    {"role": "user", "content": record.question},
                    {"role": "assistant", "content": teachers[record.id].output},
                ],
                "metadata": {"input_id": record.id, "source": "manual_teacher"},
            }
            for record in self.inputs.read_all()
            if record.id in teachers
        ]
        destination = self.data_dir / "dataset_sft.jsonl"
        with self._write_lock:
            write_jsonl(destination, dataset)
        return destination, len(dataset)
