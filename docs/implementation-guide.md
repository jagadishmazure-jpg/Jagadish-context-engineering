# Implementation guide for adopters

1. **Measure first.** Copy the benchmark pattern: a seeded task suite with known answers, one loop shared by all
   strategies, and tokens charged from what the model actually received, including helper calls. Without that, the
   cheapest strategy always looks best.
2. **Allocate the window explicitly.** Start from `budget.Policy`: reserve output tokens, give each section a floor and
   share the rest by weight. Redistribute slack so the window is not wasted.
3. **Compact history with a summarizer you have tested on every phrasing your tools emit.** The v1/v2 rows show how
   much one unparsed phrasing costs (45% vs 82.5% here).
4. **Prune tool results** to fields the task needs before they enter history. Keep the raw result offloaded so it can be re-read.
5. **Offload large payloads** behind opaque handles in a sandboxed directory. Retrieve by query at answer time.
6. **Pass deltas between agents** with a base version, and resync on any gap. Never assume delivery.
7. **Add a critic** only for error classes it can detect. Cap retries (one was enough here) and put its cost in the eval gate.
8. **Mask PII** in every log handler and exception path before text leaves the process.

Swapping in a real model: implement `answer(context, keys, seed, careful)` and `visible(context)` with the same
contract, keep the fake for CI, and mark real-model numbers separately.
