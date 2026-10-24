from ctxeng import tokens
from ctxeng.model import FakeModel
from ctxeng.tasks import facts_in, make_task, suite


def test_tasks_are_deterministic():
    assert make_task(3).steps == make_task(3).steps


def test_tasks_are_long_multi_step():
    for t in suite(10):
        assert 30 <= len(t.steps) <= 60
        assert sum(tokens.count(s) for s in t.steps) > 3000


def test_truth_is_latest_value_in_full_text():
    for t in suite(10):
        last = {}
        for e, a, v in facts_in("\n".join(t.steps)):
            last[(e, a)] = v
        for k in t.goal_keys:
            assert last[k] == t.truth[k]


def test_goal_names_all_keys():
    t = make_task(1)
    for e, a in t.goal_keys:
        assert f"{a} of {e}" in t.goal


def test_both_fact_phrasings_parsed():
    txt = "RECORD acct-01 status = open . note: acct-01 status changed to closed ."
    assert facts_in(txt) == [("acct-01", "status", "open"), ("acct-01", "status", "closed")]


def test_window_truncates_front():
    m = FakeModel(window=5)
    assert m.visible("a b c d e f g") == "c d e f g"


def test_model_charges_visible_tokens_only():
    m = FakeModel(window=5)
    m.call("a b c d e f g")
    assert m.input_tokens == 5 and m.calls == 1


def test_model_reads_latest_short_context():
    m = FakeModel(careless=0.0)
    ctx = "RECORD acct-01 status = open . RECORD acct-01 status = closed ."
    assert m.answer(ctx, [("acct-01", "status")], seed=1)[("acct-01", "status")] == "closed"


def test_model_returns_none_when_fact_cut():
    m = FakeModel(window=4)
    ctx = "RECORD acct-01 status = open . filler filler filler filler"
    assert m.answer(ctx, [("acct-01", "status")], seed=1)[("acct-01", "status")] is None


def test_careless_mode_is_deterministic_and_bypassed_when_careful():
    m = FakeModel(careless=1.0)
    ctx = "RECORD acct-01 status = open . RECORD acct-01 status = closed ."
    k = ("acct-01", "status")
    assert m.answer(ctx, [k], seed=1)[k] == "open"
    assert m.answer(ctx, [k], seed=1, careful=frozenset({k}))[k] == "closed"


def test_no_miss_on_short_context():
    m = FakeModel(max_miss=1.0, careless=0.0)
    ctx = "RECORD acct-01 status = open ."
    assert m.answer(ctx, [("acct-01", "status")], seed=9)[("acct-01", "status")] == "open"


def test_clip_helpers():
    assert tokens.clip("a b c", 2) == "a b"
    assert tokens.clip_tail("a b c", 2) == "b c"
    assert tokens.clip_tail("a b c", 0) == ""
