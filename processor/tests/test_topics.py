import pytest
from unittest.mock import MagicMock
from confluent_kafka.admin import NewTopic, NewPartitions
from processor.topics import discover_topics, get_topic_names, create_interval_topics
from processor.config import DESIRED_PARTITIONS, WINDOW_CONFIGS


def test_discover_topics(monkeypatch):
    fake_admin = MagicMock()
    # first call returns empty, second returns metadata with topics dict
    fake_md1 = MagicMock(topics=None)
    fake_md2 = MagicMock(topics={'trades.A': None, 'other': None})
    fake_admin.list_topics.side_effect = [fake_md1, fake_md2]
    topics = discover_topics(fake_admin)
    assert 'trades.A' in topics


def test_get_topic_names():
    class MD:
        def __init__(self, topics): self.topics = topics
    md = MD(topics=['trades.X', 'foo', 'trades.Y'])
    names = get_topic_names(md)
    assert sorted(names) == ['trades.X', 'trades.Y']


def test_create_interval_topics_new(monkeypatch):
    fake_admin = MagicMock()
    # simulate no existing topics
    topics = {}
    create_interval_topics(fake_admin, topics)
    # expect create_topics for each interval
    calls = [call[0][0].name for call in fake_admin.create_topics.call_args_list]
    expected = [f"candles.{label}" for label, _ in WINDOW_CONFIGS]
    assert sorted(calls) == sorted(expected)