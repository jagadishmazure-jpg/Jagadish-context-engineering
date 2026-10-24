# Architecture

```mermaid
flowchart TB
  subgraph Inputs
    G[tasks.py<br/>seeded synthetic tasks]
  end
  subgraph Strategies[strategies.py]
    N[naive]
    C1[compaction v1]
    C2[compaction v2]
    P[tool pruning]
    O[offload + grep]
    B[budgeted: allocator over 4 sections]
  end
  G --> Strategies --> FM[model.py FakeModel<br/>window 1,200, distraction, carelessness]
  FM --> CR[critic.py<br/>bounded retries]
  CR --> BE[bench.py<br/>accuracy, Wilson CI, tokens]
  BE --> CLI[cli.py ctxeng demo] --> RD[scripts/render_docs.py<br/>README + docs numbers]
  O <--> SC[offload.py Scratch<br/>private temp dir]
  D[deltas.py<br/>versioned deltas + resync] --> BE
  PII[pii.py masking filter] -.-> CLI
```

| module | responsibility |
| --- | --- |
| `tokens.py` | word-count tokens, head and tail clipping |
| `budget.py` | floors, weights, output reserve, slack redistribution |
| `tasks.py` | task generator and fact parsers, for both phrasings |
| `model.py` | deterministic fake reader with stated weaknesses |
| `strategies.py` | the six context builders and the shared agent loop |
| `offload.py` | scratch files with safe handles and grep |
| `deltas.py` | full vs delta hand-off, gap detection, resync |
| `critic.py` | stale-value critic, retry cap, cost accounting |
| `pii.py` | masking for logs and errors |
| `bench.py`, `cli.py` | tables printed by `ctxeng demo` |

Key decisions are in [adr/](adr/).
