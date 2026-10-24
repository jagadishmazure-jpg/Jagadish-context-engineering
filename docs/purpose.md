# Purpose and audience

Agents that run for dozens of steps hit one practical wall: the model can only see a fixed window, and
whatever is in that window competes for its attention. "Context engineering" is the work of deciding,
call by call, what goes in.

This repo turns that work into measurable code. Each technique is a small module with tests, and one
benchmark scores all of them on the same tasks so the trade-offs are visible as numbers instead of opinions.

**Who it is for**

| reader | what to look at |
| --- | --- |
| Agent engineers | `src/ctxeng/strategies.py`, `budget.py`, `critic.py` |
| Reviewers / interviewers | README results tables, `docs/interview-points.md` |
| Adopters | `docs/implementation-guide.md` |

**Out of scope:** real model calls, real tokenizers and production storage. See `limitations.md`.
