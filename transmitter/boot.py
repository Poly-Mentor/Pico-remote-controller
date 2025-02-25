import network
import asyncio

asyncio.new_event_loop()
wlan = network.WLAN(network.STA_IF)
wlan.active(False)