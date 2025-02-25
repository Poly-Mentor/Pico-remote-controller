""" MIT License
Copyright (c) 2025 Filip S. (polymentor@proton.me)"""

from machine import Pin, ADC
from time import sleep_ms

class Joystick():
    
    def __init__(self, XaxisPinNumber: int, \
                 YaxisPinNumber: int, \
                 ButtonPinNumber: int, \
                 reverseX = False, \
                 reverseY = True):
        
        self._Xpin = Pin(XaxisPinNumber)
        self._Xpot = ADC(self._Xpin)

        self._Ypin = Pin(YaxisPinNumber)
        self._Ypot = ADC(self._Ypin)

        self.ButtonPin = Pin(ButtonPinNumber, Pin.IN, Pin.PULL_UP)
        # position values
        self.X = 0
        self.Y = 0
        # reversing settings
        self.reverseX = reverseX
        self.reverseY = reverseY
        # calibration values
        self._XrestVal = 31500
        self._YrestVal = 34000
        self._Xdeadzone = 600
        self._Ydeadzone = 500
        self._Xmin = 200
        self._Ymin = 200
        self._Xmax = 65500
        self._Ymax = 65500

    def read(self):
        rawXvalue = self._Xpot.read_u16()
        rawYvalue = self._Ypot.read_u16()
        #if raw value is within deadzone, set to 0
        if rawXvalue < self._XrestVal + self._Xdeadzone and rawXvalue > self._XrestVal - self._Xdeadzone:
            self.X = 0
        else:
            # remap to range [-100, 100]
            self.X = max(rawXvalue - self._Xmin, 0) * 200 // (self._Xmax - self._Xmin) - 100
            if self.reverseX:
                self.X = -self.X
        if rawYvalue < self._YrestVal + self._Ydeadzone and rawYvalue > self._YrestVal - self._Ydeadzone:
            self.Y = 0
        else:
            self.Y = max(rawYvalue - self._Ymin, 0) * 200 // (self._Ymax - self._Ymin) - 100
            if self.reverseY:
                self.Y = -self.Y

    def test(self):
        while True:
            self.read()
            print(f"X = {self.X}, Y = {self.Y}")
            sleep_ms(250)
