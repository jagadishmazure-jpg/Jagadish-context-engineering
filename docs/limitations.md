# Limitations and known failures

- **Fake model.** The window, the distraction curve (0-15% line misses) and the 25% carelessness rate are assumptions
  chosen to make failure modes visible. They are not measured from any real model.
- **Token counting** is whitespace words. A real tokenizer would give different absolute numbers, but similar ratios.
- **Small set.** 40 tasks. The Wilson intervals are wide (for example 68-91% for compaction v2). Treat the table as a regression check.
- **Compaction v1 phrasing gap** (kept as a test). The extractive summarizer ignores `note: ... changed to ...`, so
  facts written that way are lost once their step is compacted.
- **Critic ceiling.** The critic fixes stale answers only. In the run, a second retry costs tokens and adds no accuracy.
- **Pruning grows** with step count. Over 60 steps the pruned context still overflows the window on some tasks.
- **Offload depends on the grep.** If the goal named a key by a synonym, the grep would miss it.
- **Delta loss on the final hop** is only detected when the next message arrives.
- **No real model runner** exists yet.
