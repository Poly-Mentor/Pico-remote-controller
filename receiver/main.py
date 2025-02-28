import asyncio

async def someCode():
    while True:
        # other code to run
        await asyncio.sleep(1)


async def main():
    pass

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print('Interrupted')
finally:
    asyncio.new_event_loop() # Clear retained state