from ctxeng.bench import critic_table, strategy_table, wilson
from ctxeng.cli import main


def test_wilson_bounds():
    lo, hi = wilson(0, 40)
    assert lo == 0 and 0 < hi < 0.1
    assert wilson(0, 0) == (0.0, 0.0)


def test_strategy_table_small_run():
    rows = strategy_table(4)
    assert rows[0]["strategy"] == "naive_full_context"
    assert all(0 <= r["accuracy"] <= 1 for r in rows)


def test_critic_cost_check_under_ten_percent():
    rows = critic_table(8)
    assert rows[-1]["tokens_per_task"] / rows[0]["tokens_per_task"] - 1 < 0.10


def test_cli_usage():
    assert main([]) == 2


def test_cli_demo_prints_tables(capsys):
    assert main(["demo"]) == 0
    out = capsys.readouterr().out
    assert "naive_full_context" in out and "max critic retries" in out
