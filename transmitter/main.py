import asyncio
import network

SSID = "Pico transmitter"
PASSWORD = "pleasepicoworkthistime"

def initNetwork():
    print("Initializing network")
    wlan = network.WLAN(network.IF_AP)
    network.hostname("transmitter")
    wlan.config(ssid=SSID, key=PASSWORD)
    wlan.active(True)
    print("Network initialized")

def get_connected_clients(wlan):
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
            clients = new_clients
        await asyncio.sleep(1)

async def main():
    initNetwork()
    await connection_detector()

# ------------------------------------------------------

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print('Interrupted')
finally:
    asyncio.new_event_loop()  # Clear retained state