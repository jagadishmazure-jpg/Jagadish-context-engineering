"""Passing only deltas between agents.

A planner, a worker and a reviewer share a state dict. The naive hand-off serialises the whole state on
every hop. The delta hand-off sends only keys that changed since the receiver's last acknowledged
version. A receiver that sees a version gap refuses the delta and asks for a full resync, so a lost
message can never leave two agents silently disagreeing.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, field

from . import tokens

DELETED = "__deleted__"


@dataclass
class Peer:
    name: str
    state: dict = field(default_factory=dict)
    version: int = 0

    def apply(self, msg: dict) -> bool:
        if msg["kind"] == "full":
            self.state = dict(msg["state"])
            self.version = msg["version"]
            return True
        if msg["base"] != self.version:
            return False  # gap: caller must resync
        for k, v in msg["changes"].items():
            if v == DELETED:
                self.state.pop(k, None)
            else:
                self.state[k] = v
        self.version = msg["version"]
        return True


def diff(old: dict, new: dict) -> dict:
    ch = {k: v for k, v in new.items() if old.get(k) != v}
    ch.update({k: DELETED for k in old if k not in new})
    return ch


def full_msg(state: dict, version: int) -> dict:
    return {"kind": "full", "version": version, "state": state}


def delta_msg(old: dict, new: dict, base: int, version: int) -> dict:
    return {"kind": "delta", "base": base, "version": version, "changes": diff(old, new)}


def size(msg: dict) -> int:
    return tokens.count(json.dumps(msg, sort_keys=True).replace(",", " ").replace(":", " "))


def simulate(hops: int = 60, seed: int = 7, drop_every: int = 0) -> dict:
    """Run one shared-state conversation with both hand-off styles. Returns token totals and checks."""
    rng = random.Random(seed)
    state: dict = {f"plan.{i}": "todo" for i in range(25)}
    state.update({f"fact.{i}": f"value-{i}" for i in range(25)})
    receiver_full, receiver_delta = Peer("worker-full"), Peer("worker-delta")
    # Both receivers start from one full snapshot (version 0); after that only messages flow.
    receiver_full.apply(full_msg(dict(state), 0))
    receiver_delta.apply(full_msg(dict(state), 0))
    sent_full = sent_delta = resyncs = 0
    history = {0: dict(state)}
    last_sent = 0  # sender is optimistic: it diffs against what it last SENT, not what was received
    for hop in range(1, hops + 1):
        for _ in range(rng.randint(1, 3)):
            k = rng.choice(sorted(state))
            state[k] = f"{state[k].split('#')[0]}#{hop}"
        if hop % 17 == 0:
            state.pop(rng.choice(sorted(state)))
        history[hop] = dict(state)
        m = full_msg(dict(state), hop)
        sent_full += size(m)
        receiver_full.apply(m)
        d = delta_msg(history[last_sent], state, last_sent, hop)
        sent_delta += size(d)
        last_sent = hop
        if drop_every and hop % drop_every == 0:
            continue  # lost in transit; the receiver never sees it
        if not receiver_delta.apply(d):
            resyncs += 1
            f = full_msg(dict(state), hop)
            sent_delta += size(f)
            receiver_delta.apply(f)
    return {
        "hops": hops,
        "full_tokens": sent_full,
        "delta_tokens": sent_delta,
        "resyncs": resyncs,
        "full_in_sync": receiver_full.state == state,
        "delta_in_sync": receiver_delta.state == state,
    }
