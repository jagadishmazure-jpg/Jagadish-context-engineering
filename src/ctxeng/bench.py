"""Benchmark: accuracy vs tokens for every strategy on the same synthetic suite."""

from __future__ import annotations

import math

from .critic import run_with_critic
from .deltas import simulate
from .strategies import STRATEGIES, run_task
from .tasks import suite

N_TASKS = 40


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def strategy_table(n: int = N_TASKS) -> list[dict]:
    tasks = suite(n)
    rows = []
    for name in STRATEGIES:
        res = [run_task(name, t) for t in tasks]
        k = sum(r["correct"] for r in res)
        tok = sum(r["tokens"] for r in res)
        lo, hi = wilson(k, n)
        rows.append(
            {
                "strategy": name,
                "correct": k,
                "n": n,
                "accuracy": k / n,
                "ci": (lo, hi),
                "tokens_per_task": tok / n,
                "final_ctx": sum(r["final_ctx_tokens"] for r in res) / n,
            }
        )
    return rows


def critic_table(n: int = N_TASKS, strategy: str = "compaction_v2") -> list[dict]:
    tasks = suite(n)
    rows = []
    for retries in (0, 1, 2):
        res = [run_with_critic(strategy, t, max_retries=retries) for t in tasks]
        k = sum(r["correct"] for r in res)
        rows.append(
            {
                "max_retries": retries,
                "correct": k,
                "n": n,
                "accuracy": k / n,
                "tokens_per_task": sum(r["tokens"] for r in res) / n,
                "retries_used": sum(r["retries"] for r in res),
            }
        )
    return rows


def delta_table() -> list[dict]:
    return [simulate(drop_every=0) | {"case": "no loss"}, simulate(drop_every=9) | {"case": "every 9th delta lost"}]
