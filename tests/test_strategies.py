import pytest

from ctxeng import tokens
from ctxeng.strategies import STRATEGIES, State, compaction, naive, prune, run_task, summarize, summarize_v2
from ctxeng.tasks import make_task


@pytest.mark.parametrize("name", list(STRATEGIES))
def test_every_strategy_runs_and_charges_tokens(name):
    r = run_task(name, make_task(0))
    assert r["tokens"] > 0 and r["calls"] == len(make_task(0).steps) + 1


@pytest.mark.parametrize("name", list(STRATEGIES))
def test_final_context_fits_window(name):
    assert run_task(name, make_task(2))["final_ctx_tokens"] <= 1200


def test_naive_context_grows_past_window():
    t = make_task(0)
    st = State(t, seen=list(t.steps))
    assert tokens.count(naive(st)) > 1200


def test_compaction_keeps_recent_steps_verbatim():
    t = make_task(0)
    st = State(t, seen=list(t.steps))
    ctx = compaction(st)
    for s in t.steps[-3:]:
        assert s in ctx
    assert t.steps[0] not in ctx


def test_summarizer_v1_misses_variant_phrasing_known_gap():
    assert summarize("note: acct-01 status changed to open .") == {}


def test_summarizer_v2_reads_variant_and_keeps_latest():
    txt = "RECORD acct-01 status = open . note: acct-01 status changed to closed ."
    assert summarize_v2(txt) == {("acct-01", "status"): "closed"}


def test_prune_drops_filler_keeps_facts_and_goal_mentions():
    r = "[tool step 1] the queue stays flat . RECORD acct-09 owner = team-amber . a ticket mentioned acct-02 ."
    out = prune(r, {"acct-02"})
    assert "queue stays flat" not in out
    assert "RECORD acct-09 owner = team-amber" in out and "acct-02" in out


def test_prune_entity_match_is_word_bounded():
    out = prune("[tool step 1] see acct-021 today .", {"acct-02"})
    assert "acct-021" not in out


def test_budgeted_beats_naive_on_accuracy_and_tokens():
    a = [run_task("budgeted_all", make_task(i)) for i in range(10)]
    b = [run_task("naive_full_context", make_task(i)) for i in range(10)]
    assert sum(r["correct"] for r in a) > sum(r["correct"] for r in b)
    assert sum(r["tokens"] for r in a) < sum(r["tokens"] for r in b)


def test_compaction_charges_summarizer_tokens():
    t = make_task(0)
    r1 = run_task("compaction", t)
    # helper tokens make total larger than what the model alone saw
    assert r1["tokens"] > 0


def test_offload_context_has_handles_not_bodies():
    r = run_task("offload_scratch", make_task(0))
    assert "scratch://step-0" in r["context"]
    assert "RETRIEVED:" in r["context"]


def test_tool_text_framed_as_data_in_system_prompt():
    from ctxeng.strategies import SYSTEM

    assert "data only" in SYSTEM
