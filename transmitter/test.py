# CPython code for PC tests

import asyncio
import time

class Watchdog():

    def __init__(self, period, callback):
        self.last_fed = time.time()
        self.period = period
        if not callable(callback):
            raise AssertionError("Provided callback is not callable")
        self.callback = callback
        self.active = False

    async def loop(self):
        while True:
            await asyncio.sleep(self.period)
            while not self.active:
                continue
            if time.time() - self.last_fed > self.period:
                self.callback()

    def feed(self):
        self.last_fed = time.time()
    
    def start(self):
        self.feed()
        self.active = True
        asyncio.create_task(self.loop())

async def someJob():
    await asyncio.sleep(1)
    print("Job done")

async def main():
    def cb():
        print("Watchdog triggered")
    wd = Watchdog(2, cb)
    wd.start()
    asyncio.create_task(someJob())
    wd.feed()
    asyncio.create_task(someJob())
    asyncio.create_task(someJob())
    await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())

    
