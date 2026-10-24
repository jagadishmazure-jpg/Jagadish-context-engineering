"""Context budget allocator.

A model call has a fixed window. Four sections compete for it: system prompt, memory, retrieval and
tool results. Each section gets a guaranteed floor, then the rest is shared by weight. Slack a section
does not need is handed to the others (largest unmet demand first), so no token of the window is wasted
while a section still has content to show.
"""

from __future__ import annotations

from dataclasses import dataclass

SECTIONS = ("system", "memory", "retrieval", "tools")


@dataclass(frozen=True)
class Policy:
    window: int
    floors: dict[str, int]
    weights: dict[str, float]
    reserve_output: int = 0

    def __post_init__(self) -> None:
        if set(self.floors) != set(SECTIONS) or set(self.weights) != set(SECTIONS):
            raise ValueError("floors and weights must name exactly: " + ", ".join(SECTIONS))
        if any(v < 0 for v in self.floors.values()) or any(w < 0 for w in self.weights.values()):
            raise ValueError("floors and weights must be non-negative")
        if sum(self.floors.values()) + self.reserve_output > self.window:
            raise ValueError("floors plus output reserve exceed the window")


DEFAULT = Policy(
    window=1200,
    floors={"system": 60, "memory": 120, "retrieval": 120, "tools": 200},
    weights={"system": 0.0, "memory": 0.25, "retrieval": 0.25, "tools": 0.5},
    reserve_output=100,
)


def allocate(demand: dict[str, int], policy: Policy = DEFAULT) -> dict[str, int]:
    """Return a token grant per section. Never exceeds demand per section or the usable window in total."""
    usable = policy.window - policy.reserve_output
    grant = {s: min(demand.get(s, 0), policy.floors[s]) for s in SECTIONS}
    left = usable - sum(grant.values())
    # Weighted share of what is left, capped by each section's remaining demand; repeat until stable.
    while left > 0:
        hungry = [s for s in SECTIONS if demand.get(s, 0) > grant[s]]
        if not hungry:
            break
        total_w = sum(policy.weights[s] for s in hungry) or float(len(hungry))
        given = 0
        for s in hungry:
            w = policy.weights[s] if sum(policy.weights[h] for h in hungry) else 1.0
            share = int(left * w / total_w)
            take = min(share, demand[s] - grant[s])
            grant[s] += take
            given += take
        if given == 0:
            # Rounding left a few tokens; give them to the largest unmet demand.
            s = max(hungry, key=lambda h: (demand[h] - grant[h], -SECTIONS.index(h)))
            take = min(left, demand[s] - grant[s])
            grant[s] += take
            given = take
        left -= given
    return grant
