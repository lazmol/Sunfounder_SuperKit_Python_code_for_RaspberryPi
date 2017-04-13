#!/usr/bin/env python3

from twisted.internet import reactor
from sysfs.gpio import Controller, OUTPUT
import time


class Led():
    PIN = 57  # pin50 on J3A1

    def __init__(self):
        Controller.available_pins = [self.PIN]
        self.pin_controller = Controller.alloc_pin(self.PIN, OUTPUT)
        self.pin_controller.set()

    def loop(self):
        while True:
            print('...led on')
            self.pin_controller.reset()
            time.sleep(0.5)
            print('led off...')
            self.pin_controller.set()
            time.sleep(0.5)
        reactor.run()

    def destroy(self):
        self.pin_controller.set()
        Controller.dealloc_pin(self.PIN)
        reactor.stop()


if __name__ == '__main__':     # Program start from here
    led = Led()
    try:
        led.loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        led.destroy()
