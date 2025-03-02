import aiohttp
import asyncio
import network

SSID = "Pico transmitter"
PASSWORD = "pleasepicoworkthistime"

def initNetwork():
    print("Initializing network")
    global wlan
    wlan = network.WLAN(network.STA_IF)
    network.hostname("receiver")
    wlan.active(True)
    print("Network initialized")

async def connect():
    global wlan
    wlan.connect(SSID, PASSWORD)
    print("Waiting for connection")
    while not wlan.isconnected():
        print(wlan.status())
        await asyncio.sleep(1)
    print('network config:', wlan.ifconfig())

async def get():

    async with aiohttp.ClientSession() as session:
        async with session.get('http://192.168.4.1:5000/') as response:
            print("Status:", response.status)
            content = await response.text()
            print(content)
#             print("Status:", response.status)
#             print("Content-Type:", response.headers['Content-Type'])
# 
#             html = await response.text()
#             print("Body:", html[:15], "...")

async def main():
    initNetwork()
    await connect()
    while True:
        await get()
        await asyncio.sleep(1)

# ------------------------------------------------------

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print('Interrupted')
finally:
    wlan.disconnect()
    wlan.active(False)
    asyncio.new_event_loop()  # Clear retained state