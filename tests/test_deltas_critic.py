import pytest

from ctxeng.critic import critique, run_with_critic
from ctxeng.deltas import DELETED, Peer, delta_msg, diff, full_msg, simulate
from ctxeng.tasks import make_task


def test_diff_tracks_changes_and_deletes():
    assert diff({"a": 1, "b": 2}, {"a": 1, "b": 3, "c": 4}) == {"b": 3, "c": 4}
    assert diff({"a": 1}, {}) == {"a": DELETED}


def test_peer_rejects_version_gap():
    p = Peer("w")
    p.apply(full_msg({"a": 1}, 1))
    assert not p.apply(delta_msg({"a": 1}, {"a": 2}, base=2, version=3))
    assert p.state == {"a": 1}


def test_delta_much_smaller_and_in_sync():
    r = simulate()
    assert r["delta_in_sync"] and r["full_in_sync"]
    assert r["delta_tokens"] < 0.2 * r["full_tokens"]


def test_lost_deltas_trigger_resync_and_recover():
    r = simulate(drop_every=9)
    assert r["resyncs"] > 0 and r["delta_in_sync"]


def test_receiver_starts_from_snapshot_regression():
    # bug fixed: the delta receiver used to start empty, so it never matched the sender
    assert simulate(hops=1)["delta_in_sync"]


def test_critique_flags_stale_answer():
    ev = "RECORD acct-01 status = open . RECORD acct-01 status = closed ."
    assert critique(ev, {("acct-01", "status"): "open"}) == {("acct-01", "status")}
    assert critique(ev, {("acct-01", "status"): "closed"}) == set()


def test_critique_cannot_flag_missing_evidence():
    assert critique("", {("acct-01", "status"): None}) == set()


@pytest.mark.parametrize("cap", [0, 1, 2])
def test_retries_bounded(cap):
    for i in range(8):
        assert run_with_critic("compaction_v2", make_task(i), max_retries=cap)["retries"] <= cap


def test_negative_retries_rejected():
    with pytest.raises(ValueError):
        run_with_critic("compaction_v2", make_task(0), max_retries=-1)


def test_critic_never_hurts_and_costs_tokens():
    for i in range(10):
        a = run_with_critic("compaction_v2", make_task(i), max_retries=0)
        b = run_with_critic("compaction_v2", make_task(i), max_retries=2)
        assert b["correct"] >= a["correct"]
        assert b["tokens"] >= a["tokens"]
