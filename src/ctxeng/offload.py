"""Scratch-file offloading. Large tool results are written to a private temp directory and replaced in
context by a short handle. Handles are opaque names; paths outside the scratch root are refused."""

from __future__ import annotations

import re
import shutil
import tempfile
from pathlib import Path

SAFE = re.compile(r"^[a-z0-9-]{1,40}$")


class Scratch:
    def __init__(self, root: Path | None = None) -> None:
        self._own = root is None
        self.root = Path(tempfile.mkdtemp(prefix="ctxeng-")) if root is None else root
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, name: str) -> Path:
        if not SAFE.match(name):
            raise ValueError("scratch names must be short lowercase slugs")
        p = (self.root / f"{name}.txt").resolve()
        if p.parent != self.root.resolve():
            raise ValueError("path escapes scratch root")
        return p

    def put(self, name: str, text: str) -> str:
        p = self._path(name)
        if not p.exists():
            p.write_text(text)
        return f"scratch://{name}"

    def get(self, handle: str) -> str:
        if not handle.startswith("scratch://"):
            raise ValueError("not a scratch handle")
        return self._path(handle.removeprefix("scratch://")).read_text()

    def grep(self, terms: list[str]) -> list[str]:
        """Sentences from all scratch files mentioning any term, in step order."""
        out = []
        files = sorted(self.root.glob("step-*.txt"), key=lambda p: int(p.stem.split("-")[1]))
        for f in files:
            for s in f.read_text().split(" ."):
                if any(re.search(rf"\b{re.escape(t)}\b", s) for t in terms):
                    out.append(s.strip() + " .")
        return out

    def close(self) -> None:
        if self._own:
            shutil.rmtree(self.root, ignore_errors=True)
