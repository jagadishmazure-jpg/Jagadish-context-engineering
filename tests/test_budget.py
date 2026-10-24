import pytest

from ctxeng.budget import DEFAULT, SECTIONS, Policy, allocate


def test_never_exceeds_usable_window():
    g = allocate({s: 10_000 for s in SECTIONS})
    assert sum(g.values()) == DEFAULT.window - DEFAULT.reserve_output


def test_never_exceeds_demand():
    d = {"system": 30, "memory": 5, "retrieval": 0, "tools": 50}
    assert allocate(d) == d


def test_floors_respected_under_pressure():
    g = allocate({s: 10_000 for s in SECTIONS})
    for s in SECTIONS:
        assert g[s] >= DEFAULT.floors[s]


def test_slack_redistributed_to_hungry_section():
    g = allocate({"system": 40, "memory": 0, "retrieval": 0, "tools": 5000})
    assert g["tools"] == DEFAULT.window - DEFAULT.reserve_output - 40


def test_weights_split_remainder():
    g = allocate({s: 10_000 for s in SECTIONS})
    assert g["tools"] > g["memory"] >= g["system"]


def test_zero_weights_still_allocate():
    p = Policy(100, {s: 0 for s in SECTIONS}, {s: 0.0 for s in SECTIONS})
    g = allocate({s: 100 for s in SECTIONS}, p)
    assert sum(g.values()) == 100


@pytest.mark.parametrize(
    "kw",
    [
        {"floors": {"system": 1}},
        {"floors": {"system": 2000, "memory": 0, "retrieval": 0, "tools": 0}},
        {"weights": {"system": -1, "memory": 0, "retrieval": 0, "tools": 0}},
    ],
)
def test_bad_policy_rejected(kw):
    args = {"window": 1000, "floors": {s: 0 for s in SECTIONS}, "weights": {s: 1.0 for s in SECTIONS}} | kw
    with pytest.raises(ValueError):
        Policy(**args)


def test_missing_section_demand_is_zero():
    g = allocate({"tools": 10})
    assert g == {"system": 0, "memory": 0, "retrieval": 0, "tools": 10}


def test_readme_excerpt_output_is_real():
    from pathlib import Path

    g = allocate({"system": 45, "memory": 300, "retrieval": 900, "tools": 4000})
    assert g == {"system": 45, "memory": 273, "retrieval": 273, "tools": 509}
    assert str(g) in (Path(__file__).resolve().parents[1] / "README.md").read_text()
