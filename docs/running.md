# Running

## Offline (the only mode)

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
ruff check . && ruff format --check .
pytest -q
python scripts/count_tests.py
ctxeng demo
python scripts/render_docs.py --check
python scripts/check_brands.py
```

The demo takes about 7 seconds on a laptop. It needs no keys and no network.

## Optional real model

Not written yet. A runner would replace `FakeModel.answer` with a local model call, such as a small model served on
localhost, and stay skipped in CI. Until it exists, no number in this repo describes a real model.

## Originality check

`python scripts/overlap_check.py /path/to/reference.txt` reports any 8-word run shared with a reference text. The
references are never committed.
