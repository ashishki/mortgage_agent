# modules/notifier.py
"""
Send notifications for records needing manual review (e.g., via Slack webhook).
"""
import os
import requests
from typing import Dict

class Notifier:
    def __init__(self, config: Dict):
        """
        Initialize notifier with configuration.

        Args:
            config: Dict containing 'slack': {'webhook_url': str}
        """
        self.webhook_url = (
            os.environ.get('SLACK_WEBHOOK_URL')
            or config.get('slack', {}).get('webhook_url')
        )
        if not self.webhook_url:
            raise ValueError("Notifier requires a Slack webhook URL in config or SLACK_WEBHOOK_URL env")

    def notify(self, record: Dict[str, str]) -> None:
        """
        Send a notification about a record needing review.

        Args:
            record: The record dict with missing fields.
        """
        # Build a simple message summarizing the record
        msg = {
            'text': f":warning: A mortgage statement needs review:\n```{record}```"
        }
        response = requests.post(self.webhook_url, json=msg)
        response.raise_for_status()

# tests/test_notifier.py
import pytest
from modules.notifier import Notifier
import requests

class DummyResponse:
    def __init__(self, status_code=200):
        self.status_code = status_code
    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} Error")

@pytest.fixture(autouse=True)
def patch_requests(monkeypatch):
    # Monkeypatch requests.post to return DummyResponse
    monkeypatch.setattr(requests, 'post', lambda url, json: DummyResponse())
    yield


def test_notify_success(monkeypatch, tmp_path):
    # Provide webhook via config
    cfg = {'slack': {'webhook_url': 'https://hooks.slack.com/services/XXX/YYY/ZZZ'}}
    notifier = Notifier(cfg)
    record = {'StatementDate': '2025-03-18', 'AmountPrincipal': '1605.00'}
    # Should not raise
    notifier.notify(record)


def test_missing_webhook_raises():
    with pytest.raises(ValueError):
        Notifier({})
