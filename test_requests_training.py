import requests_training as fetcher
import requests
import pytest
import logging

class FakeResponse:
    def __init__(self, status_code=200):
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(response=self)


def test_success(monkeypatch):
    def fake_get(url, timeout):
        return FakeResponse()

    monkeypatch.setattr(fetcher.requests, "get", fake_get)

    r = fetcher.fetch("https://x.test")

    assert r.status_code == 200

def test_timeout_then_success(monkeypatch):
    monkeypatch.setattr(fetcher.time, "sleep", lambda s: None)

    calls = []

    def fake_get(url, timeout):
        calls.append(1)
        if len(calls) == 1:
            raise requests.exceptions.ReadTimeout()
        return FakeResponse()

    monkeypatch.setattr(fetcher.requests, "get", fake_get)

    r = fetcher.fetch("https://x.test")

    assert r.status_code == 200
    assert len(calls) == 2

def test_404_not_retried(monkeypatch):
    monkeypatch.setattr(fetcher.time, "sleep", lambda s: None)

    calls = []

    def fake_get(url, timeout):
        calls.append(1)
        return FakeResponse(404)

    monkeypatch.setattr(fetcher.requests, "get", fake_get)

    with pytest.raises(fetcher.FetchHTTPError):
        fetcher.fetch("https://x.test")

    assert len(calls) == 1

def test_500_always(monkeypatch):
    monkeypatch.setattr(fetcher.time, "sleep", lambda s: None)

    calls = []

    def fake_get(url, timeout):
        calls.append(1)
        return FakeResponse(500)

    monkeypatch.setattr(fetcher.requests, "get", fake_get)

    with pytest.raises(fetcher.FetchHTTPError):
        fetcher.fetch("https://x.test")

    assert len(calls) == 3

def test_connection_error_always(monkeypatch):
    sleeps = []
    monkeypatch.setattr(fetcher.time, "sleep", sleeps.append)

    calls = []

    def fake_get(url, timeout):
        calls.append(1)
        raise requests.exceptions.ConnectionError()

    monkeypatch.setattr(fetcher.requests, "get", fake_get)

    with pytest.raises(fetcher.FetchConnectionError):
        fetcher.fetch("https://x.test")

    assert len(calls) == 3
    assert sleeps == [1, 2]

def test_failed_attempts_are_logged(monkeypatch, caplog):
    monkeypatch.setattr(fetcher.time, "sleep", lambda s: None)

    def fake_get(url, timeout):
        raise requests.exceptions.ReadTimeout()

    monkeypatch.setattr(fetcher.requests, "get", fake_get)

    with caplog.at_level(logging.WARNING):
        with pytest.raises(fetcher.FetchTimeout):
            fetcher.fetch("https://x.test")

    assert len(caplog.records) == 3
    assert "Attempt 1/3" in caplog.text

def test_success_logs_nothing(monkeypatch, caplog):
    def fake_get(url, timeout):
        return FakeResponse()

    monkeypatch.setattr(fetcher.requests, "get", fake_get)

    with caplog.at_level(logging.WARNING):
        fetcher.fetch("https://x.test")

    assert caplog.records == []