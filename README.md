# alarmclock

a terminal alarm clock. set alarms from the shell, watch them count down in a
full-screen tui, get flashed at when one fires.

## quick start

    python3 -m venv .venv && source .venv/bin/activate
    pip install -e ".[dev]"
    alarm set 18:30 dinner        # rejects past times, --tom sets tomorrow
    alarm list
    alarm cancel 1
    alarm                         # opens the clock (same as: alarm run)

keys in the ui: `a` add · `d` dismiss · `s` snooze 5m · `q` quit

## storage

`~/.alarms.json`, a plain json file. no database. the ui reloads it every
second, so `alarm set` in another terminal shows up in the clock immediately.

## design notes

- **two surfaces, one core.** `core.py` has the alarm model, the json store
  and the time math, with zero ui imports. `cli.py` (typer) and `ui.py`
  (textual) are thin layers over it. that split is what makes the logic
  testable.
- **typer for commands, textual for the live view.** echoed output can't
  count down every second, a tui can. bare `alarm` opens the clock because
  the clock is the product.
- **one asyncio tick per second**, naive local time, one-shot alarms. waking
  up needs neither sub-second precision nor utc.
- **past times are rejected** so a typo can't silently schedule nothing.
  `--tom` opts into tomorrow.
- **ringing is colour + blink + terminal bell.** no audio deps, works over
  ssh. snooze bumps the alarm 5 minutes in place.
- **ids are max+1 over the file.** fine for one user on one machine.

## tests

    pytest -q

store round-trip, due detection, past/bad time rejection, formatting, the
cli flow end to end, and a headless smoke boot of the tui.

## what i'd add next

weekday recurrence, real sound, timezone awareness.
