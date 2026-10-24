"""`ctxeng demo` prints every results table from a fresh run."""

from __future__ import annotations

import sys

from .bench import critic_table, delta_table, strategy_table


def strategies_md(rows: list[dict]) -> str:
    base = rows[0]["tokens_per_task"]
    out = [
        "| strategy | correct / tasks | accuracy | 95% CI (Wilson) | tokens per task | vs naive | final context tokens |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        lo, hi = r["ci"]
        out.append(
            f"| {r['strategy']} | {r['correct']} / {r['n']} | {r['accuracy']:.1%} | {lo:.1%} - {hi:.1%} | "
            f"{r['tokens_per_task']:,.0f} | {r['tokens_per_task'] / base:.2f}x | {r['final_ctx']:,.0f} |"
        )
    return "\n".join(out)


def critic_md(rows: list[dict]) -> str:
    base = rows[0]
    out = [
        "| max critic retries | correct / tasks | accuracy | gain vs none | tokens per task | extra tokens | retries used |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        gain = (r["accuracy"] - base["accuracy"]) * 100
        extra = r["tokens_per_task"] / base["tokens_per_task"] - 1
        out.append(
            f"| {r['max_retries']} | {r['correct']} / {r['n']} | {r['accuracy']:.1%} | {gain:+.1f} pts | "
            f"{r['tokens_per_task']:,.0f} | {extra:+.1%} | {r['retries_used']} |"
        )
    return "\n".join(out)


def delta_md(rows: list[dict]) -> str:
    out = [
        "| case | hops | full-state tokens | delta tokens | saving | resyncs | receiver in sync |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        out.append(
            f"| {r['case']} | {r['hops']} | {r['full_tokens']:,} | {r['delta_tokens']:,} | "
            f"{1 - r['delta_tokens'] / r['full_tokens']:.1%} | {r['resyncs']} | {r['delta_in_sync']} |"
        )
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] != "demo":
        print("usage: ctxeng demo")
        return 2
    print("## Accuracy vs tokens (40 synthetic tasks, fake model)\n")
    print(strategies_md(strategy_table()))
    print("\n## Critic loop on compaction_v2\n")
    print(critic_md(critic_table()))
    print("\n## Delta hand-off between agents\n")
    print(delta_md(delta_table()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
