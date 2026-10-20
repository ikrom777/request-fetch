# Python Security Training

Small Python exercises built while working toward AI + cybersecurity. Each exercise has working code and tests.

## requests_training.py

HTTP fetch client built on `requests`, practised against [httpbin.org](https://httpbin.org).

**Features**
- Fetch a URL with a timeout
- Retry on timeout and server errors (5xx)
- No retry on client errors (e.g. 404)
- Logging of attempts and failures

## Tests

Written with `pytest`. Cases covered:
- Success on first try
- Timeout, then success
- 404 not retried
- Always timeout (gives up)
- 500 error handling
- Logging output

Coverage: 87%. Uncovered: the `if __name__ == "__main__":` block.

## Setup

```
pip install requests pytest pytest-cov
```

## Run

```
python requests_training.py
```

## Run tests

```
pytest
pytest --cov=requests_training --cov-report=term-missing
```

## Skills practised

- `requests`: timeouts, status codes, error handling
- `pytest`: fixtures, monkeypatch, `pytest.raises`, `capsys`/`caplog`, coverage
- Python `logging`
- Git and GitHub workflow