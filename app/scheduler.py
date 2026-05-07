import threading
from datetime import date

from app.cnb_service import sync_one_day
from app.db import get_db


class SyncScheduler:
    def __init__(self, interval_seconds: int, currencies: list[str]):
        self.interval_seconds = interval_seconds
        self.currencies = currencies
        self._stop_event = threading.Event()
        self.db_gen = get_db()

    def start(self):
        thread = threading.Thread(target=self._loop, daemon=True)
        thread.start()

    def stop(self):
        self._stop_event.set()
        
        next(self.db_gen)

    def _loop(self):
        db = next(self.db_gen)
        
        while not self._stop_event.is_set():
            today = date.today()
            result = sync_one_day(today, self.currencies, db)
            print(f"[SCHEDULER] sync result: {result}")
            self._stop_event.wait(self.interval_seconds)
