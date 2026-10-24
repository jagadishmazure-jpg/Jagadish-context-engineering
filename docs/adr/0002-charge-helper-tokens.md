# ADR 0002: Charge helper-call tokens to the strategy

**Status:** accepted

**Context.** Summaries and critics make their own model calls. Leaving them out makes compaction and reflection look free.

**Decision.** Every strategy's token bill includes the summarizer's input and the critic's evidence reads.

**Consequences.** Compaction costs 0.6x naive instead of looking far cheaper, and the critic's cost is visible and gated at under 10%.
