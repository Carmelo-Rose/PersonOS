"""Small JSONL repository helpers used by every CLI command."""

import json
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel


ModelT = TypeVar("ModelT", bound=BaseModel)


class JsonlRepository:
    """Read and append Pydantic models in a local JSONL file."""

    def __init__(self, path: Path, model_type: type[ModelT]) -> None:
        self.path = path
        self.model_type = model_type
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)

    def read_all(self) -> list[ModelT]:
        """Parse every non-empty line into the repository's model type."""
        records: list[ModelT] = []
        with self.path.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                if not line.strip():
                    continue
                try:
                    records.append(self.model_type.model_validate_json(line))
                except Exception as error:
                    raise ValueError(
                        f"Invalid JSONL record at {self.path}:{line_number}"
                    ) from error
        return records

    def append(self, record: ModelT) -> None:
        """Append one model as a compact JSON object."""
        with self.path.open("a", encoding="utf-8") as file:
            file.write(record.model_dump_json() + "\n")


def write_jsonl(path: Path, records: list[dict]) -> None:
    """Replace a JSONL file with plain dictionary records."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")
