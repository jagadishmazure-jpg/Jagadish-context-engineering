"""Reflection / critic loop with a hard retry cap.

The critic re-reads the evidence the model was shown and checks each answered key against the LAST
value present for it. If an answer is stale it sends the model back with the flagged keys (the model
then answers those carefully). It cannot conjure facts that were never in the window, so it only fixes
one error class. Retries are capped; every critic and retry token is charged to the strategy.
"""

from __future__ import annotations

from . import tokens
from .model import FakeModel
from .strategies import State, build
from .tasks import Task, facts_in


def critique(evidence: str, answer: dict) -> set[tuple[str, str]]:
    last: dict[tuple[str, str], str] = {}
    for e, a, v in facts_in(evidence):
        last[(e, a)] = v
    return {k for k, v in answer.items() if k in last and v != last[k]}


def run_with_critic(name: str, task: Task, max_retries: int = 2, model: FakeModel | None = None) -> dict:
    if max_retries < 0:
        raise ValueError("max_retries must be >= 0")
    model = model or FakeModel()
    st = State(task)
    for r in task.steps:
        st.seen.append(r)
        model.call(build(name, st, final=False))
    ctx = build(name, st, final=True)
    seed = (task.task_id, name)
    ans = model.answer(ctx, task.goal_keys, seed=seed)
    critic_tokens = 0
    retries = 0
    careful: set = set()
    evidence = model.visible(ctx)
    while retries < max_retries:
        critic_tokens += tokens.count(evidence)
        flagged = critique(evidence, ans)
        if not flagged:
            break
        careful |= flagged
        retries += 1
        ans = model.answer(ctx, task.goal_keys, seed=seed, careful=frozenset(careful))
    if st.scratch:
        st.scratch.close()
    return {
        "correct": all(ans[k] == task.truth[k] for k in task.goal_keys),
        "retries": retries,
        "tokens": model.input_tokens + st.helper_tokens + critic_tokens,
        "critic_tokens": critic_tokens,
    }
