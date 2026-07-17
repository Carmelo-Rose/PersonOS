"""Prompt templates used by the student and judge clients."""

STUDENT_SYSTEM_PROMPT = (
    "You are a helpful assistant. Answer the user's question clearly and directly."
)

JUDGE_SYSTEM_PROMPT = """\
You compare a teacher answer and a student answer for behavior distillation.
Evaluate correctness, relevance, clarity, and whether the student preserves the
teacher's useful behavior. Return only JSON with these fields:
- winner: one of "teacher", "student", or "tie"
- score: a number from 0 to 1 representing student similarity/quality
- reason: a concise explanation
"""

JUDGE_USER_TEMPLATE = """\
Question:
{question}

Teacher answer:
{teacher_output}

Student answer:
{student_output}
"""
