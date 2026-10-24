import pytest

from ctxeng.offload import Scratch


def test_put_get_roundtrip(tmp_path):
    s = Scratch(tmp_path)
    h = s.put("step-1", "hello world")
    assert h == "scratch://step-1" and s.get(h) == "hello world"


@pytest.mark.parametrize("bad", ["../etc", "a/b", "UPPER", "", "x" * 41, "step.1"])
def test_unsafe_names_rejected(tmp_path, bad):
    with pytest.raises(ValueError):
        Scratch(tmp_path).put(bad, "x")


def test_get_rejects_non_handle(tmp_path):
    with pytest.raises(ValueError):
        Scratch(tmp_path).get("/etc/passwd")


def test_grep_in_step_order(tmp_path):
    s = Scratch(tmp_path)
    s.put("step-10", "acct-01 late .")
    s.put("step-2", "acct-01 early . other .")
    assert s.grep(["acct-01"]) == ["acct-01 early .", "acct-01 late ."]


def test_put_is_idempotent(tmp_path):
    s = Scratch(tmp_path)
    s.put("step-1", "first")
    s.put("step-1", "second")
    assert s.get("scratch://step-1") == "first"


def test_owned_scratch_cleaned_up():
    s = Scratch()
    root = s.root
    s.put("step-1", "x")
    s.close()
    assert not root.exists()
