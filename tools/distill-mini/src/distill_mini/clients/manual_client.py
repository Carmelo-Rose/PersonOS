"""Manual teacher client reserved for human-entered reference answers."""

from collections.abc import Callable


class ManualClient:
    """Collect a teacher answer through an injected prompt function."""

    def __init__(self, prompt: Callable[[str], str]) -> None:
        self.prompt = prompt

    def generate(self, question: str) -> str:
        """Show the question and return the manually entered answer."""
        return self.prompt(f"Teacher answer for: {question}")
