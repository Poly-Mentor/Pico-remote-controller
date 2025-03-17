It's not really a project but a component which I needed for building remote controlled vehicle, but can be used to any project needing peer-to-peer communication between RPi Pico boards with WiFi. Something like DIY Bambu Lab's CyberBrick, although it was not my the inspiration. 

It's using two Raspberry Pi Pico 2 W boards:
- Transmitter - with joystick module connected - sets up it's own WiFi network and wait for Receiver to connect. It hosts http server ([Microdot](https://github.com/miguelgrinberg/microdot)), which returns current joystick position on request.
- Receiver - connects to transmitter's network and periodically asks for current  position.

Code is asynchronous, but it's my first experience with asyncio, so it's probably not optimal.

Thanks for:
- Miguel Grinberg for [microdot library](https://github.com/miguelgrinberg/microdot)

- Peter Hinch for [asyncio tutorial](https://github.com/peterhinch/micropython-async/)