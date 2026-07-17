"""Typer commands for the PersonOS behavior-distillation MVP."""

from typing import Annotated

import typer

from distill_mini.clients.manual_client import ManualClient
from distill_mini.clients.openai_client import MissingOpenAIKeyError
from distill_mini.service import DistillService


app = typer.Typer(
    help="Build a small local behavior-distillation dataset.",
    no_args_is_help=True,
)

service = DistillService()


@app.command()
def add(question: Annotated[str, typer.Argument(help="Test question to add.")]) -> None:
    """Add one test question to inputs.jsonl."""
    record = service.add_input(question)
    typer.echo(f"Added input {record.id}: {record.question}")


@app.command("collect-teacher")
def collect_teacher(
    mode: Annotated[
        str, typer.Option(help="Teacher collection mode. MVP supports manual only.")
    ] = "manual",
) -> None:
    """Collect missing teacher answers."""
    if mode != "manual":
        raise typer.BadParameter("Only --mode manual is supported in this MVP.")

    snapshot = service.snapshot()
    pending = [
        item["input"] for item in snapshot["items"] if item["teacher"] is None
    ]
    if not pending:
        typer.echo("No pending teacher outputs.")
        return

    client = ManualClient(typer.prompt)
    for input_record in pending:
        answer = client.generate(input_record["question"]).strip()
        if not answer:
            typer.echo(f"Skipped empty answer for {input_record['id']}.")
            continue
        service.save_teacher(input_record["id"], answer)
        typer.echo(f"Saved teacher output for {input_record['id']}.")


@app.command("collect-student")
def collect_student() -> None:
    """Generate missing student answers with the configured OpenAI model."""
    try:
        count = service.collect_students()
    except MissingOpenAIKeyError as error:
        typer.echo(f"Skipped: {error}")
        return
    if count == 0:
        typer.echo("No pending student outputs.")
        return
    typer.echo(f"Saved {count} student outputs.")


@app.command()
def compare() -> None:
    """Judge input records that have both teacher and student outputs."""
    try:
        count = service.compare()
    except MissingOpenAIKeyError as error:
        typer.echo(f"Skipped: {error}")
        return
    if count == 0:
        typer.echo("No pending teacher/student pairs to compare.")
        return
    typer.echo(f"Saved {count} comparisons.")


@app.command("export-sft")
def export_sft() -> None:
    """Export teacher answers as chat-format SFT examples."""
    destination, count = service.export_sft()
    typer.echo(f"Exported {count} SFT examples to {destination}.")


if __name__ == "__main__":
    app()
