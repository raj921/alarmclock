from datetime import datetime, timedelta

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Input, Static

from .core import Store, left, mk

SNOOZE = 5


class Clock(App):
    TITLE = "alarm clock"
    CSS = """
    #face { height: 6; content-align: center middle; text-style: bold; }
    #face.ring { color: $error; text-style: bold blink; }
    #list { padding: 0 1; }
    #in { display: none; }
    #in.on { display: block; }
    """
    BINDINGS = [
        ("a", "add", "add"),
        ("d", "dismiss", "dismiss"),
        ("s", "snooze", "snooze"),
        ("q", "quit", "quit"),
    ]

    def __init__(self, path=None):
        super().__init__()
        self.store = Store(path)
        self.ring = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(id="face")
        yield Static(id="list")
        yield Input(placeholder="HH:MM label", id="in")
        yield Footer()

    def on_mount(self):
        self.set_interval(1, self.tick)
        self.tick()

    def tick(self):
        now = datetime.now()
        self.store = Store(self.store.path)
        if self.ring and self.ring.id not in [a.id for a in self.store.rows]:
            self.ring = None
        if not self.ring:
            due = self.store.due(now)
            if due:
                self.ring = due[0]
                self.notify(f"alarm: {self.ring.label}")
        face = self.query_one("#face")
        if self.ring:
            face.add_class("ring")
            face.update(f"\n{self.ring.label}\nd dismiss · s snooze")
            self.bell()
        else:
            face.remove_class("ring")
            face.update(f"\n{now:%H:%M:%S}\n{now:%a %d %b}")
        lines = [f"{'id':>3}  {'when':<16}  {'state':>10}  label"]
        for a in sorted(self.store.rows, key=lambda a: a.at):
            lines.append(f"{a.id:>3}  {a.at:%a %d %b %H:%M}  {self.state(a, now):>10}  {a.label}")
        self.query_one("#list").update("\n".join(lines) if self.store.rows else "no alarms — press a to add one")

    def state(self, a, now):
        if self.ring and a.id == self.ring.id:
            return "ringing"
        if a.due(now):
            return "due"
        return left(a.at, now)

    def action_add(self):
        w = self.query_one("#in")
        w.add_class("on")
        w.focus()

    def action_dismiss(self):
        if self.ring:
            self.store.cancel(self.ring.id)
            self.ring = None
            self.notify("dismissed")
            self.tick()

    def action_snooze(self):
        if self.ring:
            a = next((x for x in self.store.rows if x.id == self.ring.id), None)
            if a:
                a.at = datetime.now() + timedelta(minutes=SNOOZE)
                self.store.save()
            self.ring = None
            self.notify(f"snoozed {SNOOZE}m")
            self.tick()

    def on_key(self, ev):
        if ev.key == "escape":
            w = self.query_one("#in")
            w.remove_class("on")
            w.value = ""

    async def on_input_submitted(self, ev):
        w = ev.input
        w.remove_class("on")
        w.value = ""
        parts = ev.value.strip().split(None, 1)
        if not parts:
            return
        try:
            at = mk(parts[0])
        except ValueError as e:
            self.notify(str(e), severity="error")
            return
        a = self.store.add(at, parts[1] if len(parts) > 1 else "alarm")
        self.notify(f"alarm {a.id} set")
        self.tick()
