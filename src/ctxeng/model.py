"""A deterministic fake model that reads facts out of its context window.

It is NOT a language model. It exists so every strategy can be compared on identical, repeatable
behaviour. Two modelled weaknesses (stated assumptions, not measurements of a real model):

1. Window: only the last `window` tokens are visible. Older text is simply gone.
2. Distraction: each fact line is missed with probability that grows with visible length
   (0 at 300 tokens, `max_miss` at the full window). Misses are hashed, so runs are repeatable.
3. Carelessness (answer step only): for a key seen with several values, the model sometimes reports the
   first value instead of the last. A critic can catch this; nothing can recover a fact that was cut.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from . import tokens
from .tasks import facts_in


def _h(*parts: object) -> float:
    d = hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()
    return int(d[:8], 16) / 0xFFFFFFFF


@dataclass
class FakeModel:
    window: int = 1200
    max_miss: float = 0.15
    careless: float = 0.25
    calls: int = 0
    input_tokens: int = 0

    def visible(self, context: str) -> str:
        return tokens.clip_tail(context, self.window)

    def call(self, context: str) -> str:
        """Charge one call. Returns the visible text (what the model 'read')."""
        seen = self.visible(context)
        self.calls += 1
        self.input_tokens += tokens.count(seen)
        return seen

    def answer(
        self, context: str, keys: list[tuple[str, str]], seed: object, careful: frozenset = frozenset()
    ) -> dict[tuple[str, str], str | None]:
        seen = self.call(context)
        n = tokens.count(seen)
        miss = self.max_miss * max(0.0, min(1.0, (n - 300) / max(1, self.window - 300)))
        values: dict[tuple[str, str], list[str]] = {}
        for i, (e, a, v) in enumerate(facts_in(seen)):
            if _h(seed, "miss", e, a, v, i) < miss:
                continue
            values.setdefault((e, a), []).append(v)
        out: dict[tuple[str, str], str | None] = {}
        for k in keys:
            vs = values.get(k)
            if not vs:
                out[k] = None
            elif len(vs) > 1 and k not in careful and _h(seed, "careless", *k) < self.careless:
                out[k] = vs[0]
            else:
                out[k] = vs[-1]
        return out
