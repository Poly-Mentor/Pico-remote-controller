import asyncio
from BTSerial import BTSerial

bt = BTSerial(BTSerial.ROLE_PERIPHERAL)
bt.start()

async def someCode():
    while True:
        # other code to run
        await asyncio.sleep(1)

async def main():
    other_task = asyncio.create_task(someCode())
    #send message once
    await bt.write()
    print("Finished")
    other_task.cancel()

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print('Interrupted')
finally:
    asyncio.new_event_loop()  # Clear retained state