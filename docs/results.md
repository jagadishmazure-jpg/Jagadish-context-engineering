# Results (simulated)

All numbers come from `ctxeng demo` and are rewritten by `python scripts/render_docs.py`. CI fails if they drift.
The model is a deterministic fake, so read these as a controlled comparison of strategies, not LLM benchmarks.

## Accuracy vs tokens (40 tasks)

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

## Critic loop

<!-- BEGIN:critic -->
| max critic retries | correct / tasks | accuracy | gain vs none | tokens per task | extra tokens | retries used |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | 33 / 40 | 82.5% | +0.0 pts | 30,578 | +0.0% | 0 |
| 1 | 35 / 40 | 87.5% | +5.0 pts | 31,262 | +2.2% | 7 |
| 2 | 35 / 40 | 87.5% | +5.0 pts | 31,439 | +2.8% | 12 |
<!-- END:critic -->

## Delta hand-off

<!-- BEGIN:deltas -->
| case | hops | full-state tokens | delta tokens | saving | resyncs | receiver in sync |
| --- | --- | --- | --- | --- | --- | --- |
| no loss | 60 | 6,138 | 660 | 89.2% | 0 | True |
| every 9th delta lost | 60 | 6,138 | 1,272 | 79.3% | 6 | True |
<!-- END:deltas -->

Test count at last render: <!-- BEGIN:tests -->93<!-- END:tests -->.
