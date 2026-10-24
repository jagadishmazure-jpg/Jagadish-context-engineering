"""Synthetic long multi-step tasks.

Each task is a run of tool results (mostly filler) with a few fact lines buried inside. Some facts are
overwritten later. The final question asks for the latest value of three keys named in the goal, so an
agent must keep the right facts alive across 30-60 steps. Everything is seeded and fictional.
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass, field

ATTRS = ("status", "owner", "region")
VALUES = {
    "status": ("open", "frozen", "closed", "pending", "review"),
    "owner": ("team-amber", "team-birch", "team-cedar", "team-delta", "team-ember"),
    "region": ("north", "south", "east", "west", "central"),
}
FILLER = (
    "the shift log lists routine checks with no change to any tracked record and the queue stays flat "
    "operators confirmed the batch window and noted minor latency on the reporting job which recovered "
    "a reminder was posted about the quarterly review and nobody raised a blocking concern in the thread "
    "the export finished with the usual row counts and the dashboard refresh ran on schedule overnight"
).split()

# Canonical fact form and a looser variant phrasing. Both are true facts; the variant is harder to spot.
CANON = re.compile(r"RECORD (acct-\d+) (status|owner|region) = ([\w-]+)")
VARIANT = re.compile(r"note: (acct-\d+) (status|owner|region) changed to ([\w-]+)")


@dataclass
class Task:
    task_id: int
    goal_keys: list[tuple[str, str]]
    steps: list[str]
    truth: dict[tuple[str, str], str] = field(default_factory=dict)

    @property
    def goal(self) -> str:
        asks = ", ".join(f"{a} of {e}" for e, a in self.goal_keys)
        return f"GOAL: after all steps, report the latest {asks}."


def fact_line(rng: random.Random, ent: str, attr: str, val: str, variant_rate: float) -> str:
    if rng.random() < variant_rate:
        return f"note: {ent} {attr} changed to {val} ."
    return f"RECORD {ent} {attr} = {val} ."


def make_task(task_id: int, n_steps: int | None = None, variant_rate: float = 0.2) -> Task:
    rng = random.Random(1000 + task_id)
    n = n_steps or rng.randint(30, 60)
    ents = [f"acct-{i:02d}" for i in rng.sample(range(1, 40), 8)]
    goal = [(ents[i], rng.choice(ATTRS)) for i in range(3)]
    steps: list[list[str]] = [[] for _ in range(n)]
    truth: dict[tuple[str, str], str] = {}
    # Goal facts: first value early in the run, 0-2 overwrites anywhere after it.
    for ent, attr in goal:
        first = rng.randrange(0, max(1, n // 3))
        times = sorted({first, *rng.sample(range(first + 1, n), rng.randint(0, 2))})
        for t in times:
            val = rng.choice(VALUES[attr])
            steps[t].append(fact_line(rng, ent, attr, val, variant_rate))
            truth[(ent, attr)] = val
    # Distractor facts about other keys, and mentions of goal entities with no fact in them.
    for t in range(n):
        for _ in range(rng.randint(0, 2)):
            ent, attr = rng.choice(ents[3:]), rng.choice(ATTRS)
            steps[t].append(fact_line(rng, ent, attr, rng.choice(VALUES[attr]), variant_rate))
        if rng.random() < 0.3:
            steps[t].append(f"a ticket mentioned {rng.choice(ents[:3])} but recorded nothing new .")
    out = []
    for t in range(n):
        filler = [" ".join(rng.choice(FILLER) for _ in range(12)) + " ." for _ in range(rng.randint(8, 12))]
        lines = filler + steps[t]
        rng.shuffle(lines)
        out.append(f"[tool step {t}] " + " ".join(lines))
    return Task(task_id, goal, out, truth)


def suite(n: int = 40) -> list[Task]:
    return [make_task(i) for i in range(n)]


def facts_in(text: str) -> list[tuple[str, str, str]]:
    """All facts in order of appearance, both phrasings."""
    found = [(m.start(), m.groups()) for m in CANON.finditer(text)]
    found += [(m.start(), m.groups()) for m in VARIANT.finditer(text)]
    return [g for _, g in sorted(found)]
