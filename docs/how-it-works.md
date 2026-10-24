# How it works, step by step

1. **Generate.** `make_task(i)` seeds a random generator with `1000 + i`. It picks 8 fictional accounts, three goal
   keys and 30-60 steps. Goal facts first appear in the first third of the run and may be overwritten up to twice.
   Distractor facts about other accounts, plus mentions of goal accounts that carry no fact, add noise.
2. **Loop.** For each step the result is appended to `State.seen`, and the strategy builds a context that is "sent"
   to the model. `FakeModel.call` charges only the tokens inside the window.
3. **Strategies.**
   - *naive* concatenates everything.
   - *compaction* keeps the last 3 steps verbatim and folds older steps into a `MEMORY:` block. The summarizer reads
     each step once, and those tokens are charged.
   - *pruning* keeps only sentences that contain a fact or a goal account.
   - *offload* writes every result over 40 tokens to a scratch file and keeps a handle. At answer time it greps the
     files for goal accounts and adds the hits as `RETRIEVED:`.
   - *budgeted* builds four sections (system+goal, memory, retrieval, pruned recent tools), asks `allocate()` for a
     grant per section and clips each one. Memory and system are clipped from the end; retrieval and tools keep their newest text.
4. **Answer.** The model extracts facts from what it can see. It may miss lines (distraction grows with length) and
   may report a first value instead of a last (carelessness).
5. **Critic.** The critic reads the same visible evidence, flags any key whose answer is not the last value present,
   and the model re-answers those keys carefully. It stops when nothing is flagged or the cap is reached.
6. **Score.** A task is correct only if all three keys match. `bench.py` reports accuracy, a Wilson 95% interval,
   tokens per task and the final context size.
7. **Deltas.** `simulate()` mutates a 50-key shared state for 60 hops. The full style sends the whole state each hop.
   The delta style sends changed keys with a `base` version. If a message is lost, the next delta's base does not
   match, the receiver refuses it, and the sender resends in full.
