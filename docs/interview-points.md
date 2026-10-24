# Interview points

- **Why long context fails:** in this simulation, naive full context scored 0/40. The goal facts were cut from the
  window long before the answer step, and it spent the most tokens doing it.
- **Measure helpers too:** compaction is charged for the tokens its summarizer reads. Otherwise it would look cheaper than it is.
- **One parser gap, 37.5 points:** summarizer v1 missed one phrasing (45%). v2 fixed it (82.5%).
- **Combine, then budget:** the allocator-driven combination scored 39/40 at 0.27x naive tokens.
- **Reflection has a ceiling:** one critic retry gave +5 points for +2.2% tokens. A second retry gave +0 for more tokens,
  because a critic cannot recover facts that were never seen.
- **Deltas:** 89% fewer hand-off tokens. Losing messages forces resyncs, which still cost 79% less than full-state passing in the lossy case.
- **Honesty:** the fake model's weaknesses are assumptions, there are 40 tasks, and the Wilson intervals are reported.

Current numbers:

<!-- BEGIN:strategies -->
| strategy | correct / tasks | accuracy | 95% CI (Wilson) | tokens per task | vs naive | final context tokens |
| --- | --- | --- | --- | --- | --- | --- |
| naive_full_context | 0 / 40 | 0.0% | 0.0% - 8.8% | 50,519 | 1.00x | 1,200 |
| compaction | 18 / 40 | 45.0% | 30.7% - 60.2% | 30,151 | 0.60x | 573 |
| compaction_v2 | 33 / 40 | 82.5% | 68.0% - 91.3% | 30,578 | 0.61x | 582 |
| tool_pruning | 21 / 40 | 52.5% | 37.5% - 67.1% | 16,539 | 0.33x | 625 |
| offload_scratch | 22 / 40 | 55.0% | 39.8% - 69.3% | 10,106 | 0.20x | 529 |
| budgeted_all | 39 / 40 | 97.5% | 87.1% - 99.6% | 13,394 | 0.27x | 361 |
<!-- END:strategies -->

Tests: <!-- BEGIN:tests -->93<!-- END:tests -->.
