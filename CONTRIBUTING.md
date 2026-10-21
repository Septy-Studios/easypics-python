# Contributing

Bug reports and focused pull requests are welcome.

Before opening a pull request:

```bash
python -m pip install -e ".[dev]"
pytest
ruff check .
python -m build
```

Please keep changes scoped and include tests for behavior changes.

For security issues, follow `SECURITY.md` instead of opening a public issue.
