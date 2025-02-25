""" MIT License
Copyright (c) 2025 Filip S. (polymentor@proton.me)
Micropython code for sending messages via Bluetooth LE between two Raspberry Pi Pico 2 W boards
"""

import aioble # mip.install('aioble') or from https://github.com/micropython/micropython-lib/tree/master/micropython/bluetooth/aioble
import bluetooth
import asyncio

# Bluetooth parameters
BLE_SVC_UUID = bluetooth.UUID(0x181A)
BLE_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)
BLE_APPEARANCE = 0x0300
BLE_ADVERTISING_INTERVAL = 2000
BLE_SCAN_LENGTH = 5000
BLE_INTERVAL = 30000
BLE_WINDOW = 30000

CENTRAL_DEVICE_NAME = "Pico-central"
PERIPHERAL_DEVICE_NAME = "Pico-peripheral"

# split into two distinct classes for central and peripherial?

class BTSerial():
    ROLE_CENTAL = "Central"
    ROLE_PERIPHERAL = "Peripheral"

    def __init__(self, role):
        if role not in [self.ROLE_CENTAL, self.ROLE_PERIPHERAL]:
            raise ValueError("role argument must be BTSerial.ROLE_CENTRAL or BTSerial.ROLE_PERIPHERAL")
        self.role = role
        if role == self.ROLE_CENTAL:
            self.name = CENTRAL_DEVICE_NAME
            self.targetDeviceName = PERIPHERAL_DEVICE_NAME
        else:
            self.name = PERIPHERAL_DEVICE_NAME
            self.targetDeviceName = CENTRAL_DEVICE_NAME

    def _encode_message(self, message):
        """ Encode a message to bytes """
        return message.encode('utf-8')

    def _decode_message(self, message):
        """ Decode a message from bytes """
        return message.decode('utf-8')

    async def read(self):
        '''task for central (client)'''
        if self.role != self.ROLE_CENTAL:
            raise AttributeError("read method is available only for central role")
        # Scan for a device with matching service
        print("Scanning devices")
        target_device = None
        while not target_device:
            async with aioble.scan(duration_ms=5000, interval_us=30000, window_us=30000, active=True) as scanner:
                async for result in scanner:
                    print("device found:")
                    print(f"result= {result}, result.name()={result.name()}, result.services()={result.services()}")
                    if result.name() == self.targetDeviceName \
                        and BLE_CHARACTERISTIC_UUID in result.services():
                        print(f"Matching device found: {result.name()}")
                        target_device = result.device
                        break
            await asyncio.sleep(1)
        # Connect to a device
        print("Connecting")
        connection = None
        while not connection:
            try:
                connection = await target_device.connect(timeout_ms=2000)
            except asyncio.TimeoutError:
                print("Timeout, retrying")
                await asyncio.sleep(0)
        print("Connected")
        # Get service and characteristic
        service = await connection.service(BLE_SVC_UUID)
        characteristic = await service.characteristic(BLE_CHARACTERISTIC_UUID)
        # Subscribe for notification.
        await characteristic.subscribe(notify=True)
        # Wait for notification and print data
        while True:
            data = await characteristic.notified()
            print(f"received data: {self._decode_message(data)}")
            await asyncio.sleep(0)

    async def write(self):
        '''task for peripheral (server)'''
        if self.role != self.ROLE_PERIPHERAL:
            raise AttributeError("read method is available only for peripheral role")
        # Register service
        print("Registering service")
        service = aioble.Service(BLE_SVC_UUID)
        characteristic = aioble.Characteristic(service, BLE_CHARACTERISTIC_UUID, read=True, notify=True)
        aioble.register_services(service)
        print("Service registered")
        # Advertise
        print("Connecting...")
        connection = None
        while not connection:
            connection = await aioble.advertise(
                BLE_ADVERTISING_INTERVAL,
                name=PERIPHERAL_DEVICE_NAME,
                services=[BLE_CHARACTERISTIC_UUID],
                appearance=BLE_APPEARANCE,
                manufacturer=(0xabcd, b"1234"),
            )
            await asyncio.sleep(0)
        print("connected\nsending data")
        # Write 3 messages
        for i in range(3):
            await asyncio.sleep(1)
            i += 1
            message = "Hello " + str(i)
            characteristic.write(self._encode_message(message), send_update=True)
            print(message, " written")
        print("data sent, waiting 3 seconds before shutting down")
        await asyncio.sleep(3)

