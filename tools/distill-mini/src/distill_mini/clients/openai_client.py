"""OpenAI SDK adapter used for student generation and judging."""

from openai import OpenAI

from distill_mini.models import JudgeResult
from distill_mini.prompts import JUDGE_SYSTEM_PROMPT, JUDGE_USER_TEMPLATE


class MissingOpenAIKeyError(RuntimeError):
    """Raised when an OpenAI-backed command has no configured API key."""


class OpenAIClient:
    """Minimal wrapper around the OpenAI-compatible Chat Completions API."""

    def __init__(self, api_key: str | None, base_url: str | None = None) -> None:
        if not api_key:
            raise MissingOpenAIKeyError(
                "OPENAI_API_KEY is not configured. Copy .env.example to .env."
            )
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def generate(self, model: str, system_prompt: str, user_prompt: str) -> str:
        """Generate plain text from a model."""
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Model did not return text content.")
        return content.strip()

    def judge(
        self,
        model: str,
        question: str,
        teacher_output: str,
        student_output: str,
    ) -> JudgeResult:
        """Ask the judge model for a validated structured comparison."""
        content = self.generate(
            model,
            JUDGE_SYSTEM_PROMPT,
            JUDGE_USER_TEMPLATE.format(
                question=question,
                teacher_output=teacher_output,
                student_output=student_output,
            ),
        )
        return JudgeResult.model_validate_json(self._strip_json_fence(content))

    @staticmethod
    def _strip_json_fence(content: str) -> str:
        """Remove a Markdown JSON code fence sometimes added by chat models."""
        stripped = content.strip()
        if not stripped.startswith("```"):
            return stripped

        lines = stripped.splitlines()
        if len(lines) >= 3 and lines[-1].strip() == "```":
            return "\n".join(lines[1:-1]).strip()
        return stripped
