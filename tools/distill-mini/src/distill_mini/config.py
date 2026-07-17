"""Environment and local path configuration for the distillation CLI."""

from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"


class Settings(BaseModel):
    """Runtime settings loaded from environment variables."""

    openai_api_key: str | None = None
    openai_base_url: str | None = None
    student_model: str = "gpt-4.1-mini"
    judge_model: str = "gpt-4.1-mini"


def load_settings() -> Settings:
    """Load .env values while allowing shell environment variables to win."""
    load_dotenv(PROJECT_ROOT / ".env")

    import os

    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_base_url=os.getenv("OPENAI_BASE_URL"),
        student_model=os.getenv("STUDENT_MODEL", "gpt-4.1-mini"),
        judge_model=os.getenv("JUDGE_MODEL", "gpt-4.1-mini"),
    )
