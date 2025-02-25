import asyncio
from BTSerial import BTSerial

bt = BTSerial(BTSerial.ROLE_CENTAL)

async def someCode():
    while True:
        await asyncio.sleep(1)
        print("another code running")

async def main():
    other_task = asyncio.create_task(someCode())
    # read data
    await bt.read()
    print("Execution finished")
    other_task.cancel()

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print('Interrupted')
finally:
    asyncio.new_event_loop() # Clear retained state