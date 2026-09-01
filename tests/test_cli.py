from datetime import datetime

from typer.testing import CliRunner

from alarm.cli import app
from alarm.core import mk


def use(tmp_path, monkeypatch):
    monkeypatch.setattr("alarm.core.FNAME", tmp_path / "a.json")


def test_flow(tmp_path, monkeypatch):
    use(tmp_path, monkeypatch)
    r = CliRunner()
    out = r.invoke(app, ["set", "06:30", "wake", "--tom"])
    assert out.exit_code == 0
    out = r.invoke(app, ["list"])
    assert "wake" in out.output
    out = r.invoke(app, ["cancel", "1"])
    assert out.exit_code == 0
    out = r.invoke(app, ["list"])
    assert "no alarms" in out.output


def test_past(tmp_path, monkeypatch):
    use(tmp_path, monkeypatch)
    monkeypatch.setattr(
        "alarm.cli.mk",
        lambda t, now=None, days=0: mk(t, now=datetime(2026, 1, 1, 12, 0), days=days),
    )
    out = CliRunner().invoke(app, ["set", "11:00"])
    assert out.exit_code == 1


def test_cancel_missing(tmp_path, monkeypatch):
    use(tmp_path, monkeypatch)
    out = CliRunner().invoke(app, ["cancel", "7"])
    assert out.exit_code == 1
