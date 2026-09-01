import asyncio
from datetime import datetime, timedelta

from alarm.core import Store
from alarm.ui import Clock


def test_ui(tmp_path, monkeypatch):
    monkeypatch.setattr("alarm.core.FNAME", tmp_path / "a.json")
    Store().add(datetime.now() + timedelta(days=1), "tomorrow")

    async def go():
        async with Clock().run_test() as pilot:
            await pilot.pause()
            await pilot.press("d")
            await pilot.pause()

    asyncio.run(go())
