from datetime import datetime, timedelta

import pytest

from alarm.core import Store, mk, left


def test_roundtrip(tmp_path):
    s = Store(tmp_path / "a.json")
    s.add(datetime.now() + timedelta(hours=1), "x")
    s.add(datetime.now() + timedelta(hours=2))
    s2 = Store(tmp_path / "a.json")
    assert [a.label for a in s2.rows] == ["x", "alarm"]
    assert [a.id for a in s2.rows] == [1, 2]


def test_cancel(tmp_path):
    s = Store(tmp_path / "a.json")
    s.add(datetime.now() + timedelta(hours=1))
    assert s.cancel(1)
    assert s.rows == []
    assert not s.cancel(1)


def test_mk_past():
    now = datetime(2026, 1, 1, 12, 0)
    with pytest.raises(ValueError):
        mk("11:59", now=now)


def test_mk_tom():
    now = datetime(2026, 1, 1, 12, 0)
    assert mk("12:00", now=now, days=1).day == 2


def test_mk_bad():
    for t in ["25:00", "12:60", "nope", "1:2:3"]:
        with pytest.raises(ValueError):
            mk(t)


def test_due(tmp_path):
    now = datetime(2026, 1, 1, 12, 0)
    s = Store(tmp_path / "a.json")
    s.add(now - timedelta(minutes=1), "old")
    s.add(now + timedelta(minutes=1), "next")
    assert [a.label for a in s.due(now)] == ["old"]


def test_left():
    now = datetime(2026, 1, 1)
    assert left(now + timedelta(minutes=90), now) == "1h30m"
    assert left(now + timedelta(seconds=5), now) == "0m05s"
