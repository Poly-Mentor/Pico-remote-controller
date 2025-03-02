import asyncio
import network
from microdot import Microdot

SSID = "Pico transmitter"
PASSWORD = "pleasepicoworkthistime"

app = Microdot()

def initNetwork():
    print("Initializing network")
    global wlan
    wlan = network.WLAN(network.AP_IF)
    network.hostname("transmitter")
    wlan.config(ssid=SSID, key=PASSWORD)
    wlan.active(True)
    print("Network initialized")
    print(wlan.ifconfig())

def get_connected_clients():
    """
    Gets a list of connected clients in AP mode.

    Args:
      wlan: The WLAN interface object (in AP mode).

    Returns:
      A list of tuples, where each tuple contains (IP address, MAC address) 
      of a connected client. Returns an empty list if no clients are connected.
    """
    connected_clients = []
    if wlan.active():
        # Below code is added to get list of connected clients
        for client in wlan.status('stations'):
          connected_clients.append(client)
    return connected_clients

def check_for_new_clients(new_clients, old_clients):
    for client in new_clients:
        if client not in old_clients:
            return True
    return False

async def connection_detector():
    clients = []
    while True:
        new_clients = get_connected_clients()
        if check_for_new_clients(new_clients, clients):
            print("New client connected")
        if len(new_clients) < len(clients):
            print("Client disconnected")
        clients = new_clients
        #print(clients)
        await asyncio.sleep(1)

@app.route('/')
async def index(request):
    return 'Hello, world!'

async def main():
    initNetwork()
    asyncio.create_task(connection_detector())
    asyncio.create_task(app.start_server(debug=True))
    while True:
        await asyncio.sleep(1)


# ------------------------------------------------------

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print('Interrupted')
finally:
    wlan.active(False)
    asyncio.new_event_loop()  # Clear retained state