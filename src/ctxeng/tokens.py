"""Deterministic token counting. One token = one whitespace-separated word (a stand-in for a real tokenizer)."""

from __future__ import annotations


def count(text: str) -> int:
    return len(text.split())


def clip(text: str, limit: int) -> str:
    """Keep the first `limit` tokens of text."""
    words = text.split()
    return " ".join(words[: max(0, limit)])


def clip_tail(text: str, limit: int) -> str:
    """Keep the last `limit` tokens of text (what a front-truncating window keeps)."""
    words = text.split()
    return " ".join(words[-limit:]) if limit > 0 else ""
