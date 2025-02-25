import asyncio
import network
import time

class Watchdog():

    def __init__(self, period_ms, callback):
        self.last_fed = None
        self.period_ms = period_ms
        if not callable(callback):
            raise AssertionError("Provided callback is not callable")
        self.callback = callback
        self.active = False

    async def loop(self):
        while True:
            await asyncio.sleep_ms(self.period_ms)
            while not self.active:
                continue
            if time.ticks_diff(time.ticks_ms(), self.last_fed) >= self.period_ms:
                self.callback()
    
    def feed(self):
        self.last_fed = time.ticks_ms()

    def start(self):
        self.feed()
        self.active = True
        asyncio.create_task(self.loop())


        