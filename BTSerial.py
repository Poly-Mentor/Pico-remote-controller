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
    ROLE_CENTRAL = "Central"
    ROLE_PERIPHERAL = "Peripheral"

    def __init__(self, role):
        if role not in [self.ROLE_CENTRAL, self.ROLE_PERIPHERAL]:
            raise ValueError("role argument must be BTSerial.ROLE_CENTRAL or BTSerial.ROLE_PERIPHERAL")
        self.role = role
        self.targetDevice = None
        self.connection = None
        if role == self.ROLE_CENTRAL:
            self.name = CENTRAL_DEVICE_NAME
            self.targetDeviceName = PERIPHERAL_DEVICE_NAME
        else:
            self.name = PERIPHERAL_DEVICE_NAME
            self.targetDeviceName = CENTRAL_DEVICE_NAME
    
    @property
    def connected(self):
        if self.targetDevice and self.connection:
            return self.connection.is_connected()
        return False

    def start(self):
        if self.role == self.ROLE_CENTRAL:
            self._start_central()
        else:
            self._start_peripheral()

    # def is_connected(self):
    #     if self.targetDevice is not None:
    #         return self.targetDevice.is_connected()
    #     return False

    def _start_central(self):
        pass

    def _start_peripheral(self):
        # Register service
        print("Registering service")
        self.service = aioble.Service(BLE_SVC_UUID)
        self.characteristic = aioble.Characteristic(self.service, BLE_CHARACTERISTIC_UUID, read=True, notify=True)
        aioble.register_services(self.service)
        print("Service registered")
        asyncio.create_task(self._peripheral_connect())

    def _encode_message(self, message):
        """ Encode a message to bytes """
        return message.encode('utf-8')

    def _decode_message(self, message):
        """ Decode a message from bytes """
        return message.decode('utf-8')

    async def _scan(self):
        '''central (receiver) task'''
        print("Scanning devices")
        while True:
            if not self.connected:
                print("Reconnecting - scanning...")
                async with aioble.scan(duration_ms=5000, interval_us=30000, window_us=30000, active=True) as scanner:
                    async for result in scanner:
                        # print("device found:")
                        # print(f"result= {result}, result.name()={result.name()}, result.services()={result.services()}")
                        if result.name() == self.targetDeviceName \
                            and BLE_CHARACTERISTIC_UUID in result.services():
                            print(f"Matching device found: {result.name()}")
                            self.targetDevice = result.device
                            return
            await asyncio.sleep(1)

    async def _central_connect(self):
        print("Connecting")
        connection = None
        while not connection:
            try:
                connection = await self.targetDevice.connect(timeout_ms=2000)
                break
            except asyncio.TimeoutError:
                print("Timeout, retrying")
                await asyncio.sleep(500)
        print("Connected")
        return connection
    
    async def _peripheral_connect(self):
        '''advertising task for peripheral (transmitter)'''
        while True:
            if not self.connected:
                print("Connecting...")
                async with await aioble.advertise(
                    BLE_ADVERTISING_INTERVAL,
                    name=PERIPHERAL_DEVICE_NAME,
                    services=[BLE_CHARACTERISTIC_UUID],
                    appearance=BLE_APPEARANCE,
                ) as connection:
                    self.connection = connection
                    self.targetDevice = connection.device
                    print("Connection from: ", connection.device)
                    print(f"connection dir={dir(self.connection)}")
                    await connection.disconnected(timeout_ms=None)
                self.connection = None
                self.targetDevice = None

    async def read(self):
        '''central (receiver) task'''
        # still have problems with reconnecting to restarted peripheral
        if self.role != self.ROLE_CENTRAL:
            raise AttributeError("read method is available only for central role")
        while True:
            if not self.targetDevice:
                await self._scan()
            
            connection = await self._central_connect()
            # Get service and characteristic
            service = None
            characteristic = None
            async with connection:
                while not service or not characteristic:
                    # if not connection.is_connected():
                    #     print("Connection closed - read returns")
                    #     return
                    try:
                        service = await connection.service(BLE_SVC_UUID)
                        characteristic = await service.characteristic(BLE_CHARACTERISTIC_UUID)
                    except Exception as e:
                        print("Error when getting service and characteristic: ", e)
                    finally:
                        await asyncio.sleep(1)
                
                # Subscribe for notification.
                await characteristic.subscribe(notify=True)
                # Wait for notification and print data
                while connection.is_connected():
                    try:
                        data = await characteristic.notified()
                        print(f"received data: {self._decode_message(data)}")
                    except aioble.DeviceDisconnectedError:
                        print("Device disconnected")
                        self.targetDevice = None
                        self.connection = None
                    finally:
                        await asyncio.sleep_ms(100)


    async def write(self):
        '''task for peripheral (transmitter)'''
        while True:
            if self.role != self.ROLE_PERIPHERAL:
                raise AttributeError("read method is available only for peripheral role")
          
            i = 1
            while True:
                if self.connected:
                    # condition not working correctly - doesn't recognize when client disconnects
                    message = "Hello " + str(i)
                    self.characteristic.write(self._encode_message(message), send_update=True)
                    print(message, " written")
                    i += 1
                    # print(f"connected={self.targetDevice.is_connected}")
                await asyncio.sleep(1)

