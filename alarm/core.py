import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

FNAME = Path.home() / ".alarms.json"


@dataclass
class Alarm:
    id: int
    at: datetime
    label: str = "alarm"

    def due(self, now):
        return self.at <= now


class Store:
    def __init__(self, path=None):
        self.path = Path(path) if path else FNAME
        self.rows = self.load()

    def load(self):
        if not self.path.exists():
            return []
        raw = json.loads(self.path.read_text() or "[]")
        return [Alarm(a["id"], datetime.fromisoformat(a["at"]), a.get("label", "alarm")) for a in raw]

    def save(self):
        self.path.write_text(json.dumps([{"id": a.id, "at": a.at.isoformat(), "label": a.label} for a in self.rows]))

    def add(self, at, label="alarm"):
        nid = max((a.id for a in self.rows), default=0) + 1
        a = Alarm(nid, at, label)
        self.rows.append(a)
        self.save()
        return a

    def cancel(self, nid):
        n = len(self.rows)
        self.rows = [a for a in self.rows if a.id != nid]
        if len(self.rows) != n:
            self.save()
            return True
        return False

    def due(self, now):
        return sorted([a for a in self.rows if a.due(now)], key=lambda a: a.at)


def mk(t, now=None, days=0):
    now = now or datetime.now()
    try:
        h, m = map(int, t.split(":"))
    except ValueError:
        raise ValueError(f"bad time {t!r}, want HH:MM")
    if not (0 <= h < 24 and 0 <= m < 60):
        raise ValueError(f"bad time {t!r}, want HH:MM")
    at = now.replace(hour=h, minute=m, second=0, microsecond=0) + timedelta(days=days)
    if at <= now:
        raise ValueError(f"{t} already passed, use --tom")
    return at


def left(at, now=None):
    now = now or datetime.now()
    s = max(0, int((at - now).total_seconds()))
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    if h:
        return f"{h}h{m:02d}m"
    return f"{m}m{s:02d}s"
