# Threat model

Scope: an agent that assembles context from tool output, scratch files and messages from other agents.

## STRIDE

| threat | example here | mitigation |
| --- | --- | --- |
| Spoofing | a peer sends a delta built on a version the receiver never had | `base` version check, refuse and resync |
| Tampering | tool text tells the model to ignore its goal | tool text is framed as data; pruning keeps fact sentences only |
| Repudiation | no record of what the model saw | `run_task` returns the exact final context; the token bill is per call |
| Information disclosure | PII from tool output written to logs | `pii.MaskingFilter`; errors carry no input |
| Denial of service | unbounded critic retries or context growth | retry cap; window-capped allocator |
| Elevation of privilege | a scratch handle such as `../../etc/passwd` | slug names, root containment |

## OWASP Top 10 for LLM applications (relevant items)

| item | relevance | control |
| --- | --- | --- |
| LLM01 Prompt injection | tool output enters context | data framing, pruning, offloading. These reduce exposure; they do not prevent it |
| LLM02 Sensitive information disclosure | logs | masking filter |
| LLM06 Excessive agency | not in scope | no tools with side effects here |
| LLM10 Unbounded consumption | reflection loops, long context | retry cap, cost check, budget allocator |

Residual risk: the injection controls are structural only. No classifier is used, and a real model may still follow injected text that survives pruning.
