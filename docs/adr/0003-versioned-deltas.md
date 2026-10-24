# ADR 0003: Versioned deltas with refuse-and-resync

**Status:** accepted

**Context.** Passing full state between agents is simple but costly. Bare deltas drift silently when a message is lost.

**Decision.** Each delta carries `base` and `version`. A receiver whose version does not equal `base` refuses it, and the sender resends in full.

**Consequences.** There is one extra full message per gap, and receivers never drift. Found during the build: the receiver first started with an empty state, so it was never in sync. It now starts from a version-0 snapshot, and a regression test covers this.
