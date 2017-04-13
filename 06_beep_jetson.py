#!/usr/bin/env python3

from twisted.internet import reactor
from sysfs.gpio import Controller, OUTPUT
import time


class Buzzer():
    PIN = 160  # pin40 on J3A2

    def __init__(self):
        Controller.available_pins = [self.PIN]
        self.pin_controller = Controller.alloc_pin(self.PIN, OUTPUT)
        self.pin_controller.set()

    def loop(self):
        while True:
            self.pin_controller.reset()
            time.sleep(0.5)
            self.pin_controller.set()
            time.sleep(0.5)
        reactor.run()

    def destroy(self):
        self.pin_controller.set()
        Controller.dealloc_pin(self.PIN)
        reactor.stop()


if __name__ == '__main__':
    buzz = Buzzer()
    try:
        buzz.loop()
    except KeyboardInterrupt:
        buzz.destroy()
