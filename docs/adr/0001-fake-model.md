# ADR 0001: Deterministic fake model instead of a real LLM

**Status:** accepted

**Context.** The lab must run free in CI, give identical numbers on every run, and isolate the effect of context strategy.

**Decision.** Use `FakeModel`, a fact reader with three explicit, tunable weaknesses: window, distraction and carelessness.

**Consequences.** Comparisons between strategies are fair and repeatable. Absolute accuracy says nothing about any real model.
A real-model runner, if added, must stay optional and must not be mixed into these tables.
