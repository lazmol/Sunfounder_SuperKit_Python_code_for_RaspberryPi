#!/usr/bin/env python3

from twisted.internet import reactor
from sysfs.gpio import Controller, OUTPUT, INPUT
from time import sleep


class CharLCD:
    # commands
    LCD_CLEARDISPLAY = 0x01
    LCD_RETURNHOME = 0x02
    LCD_ENTRYMODESET = 0x04
    LCD_DISPLAYCONTROL = 0x08
    LCD_CURSORSHIFT = 0x10
    LCD_FUNCTIONSET = 0x20
    LCD_SETCGRAMADDR = 0x40
    LCD_SETDDRAMADDR = 0x80

    # flags for display entry mode
    LCD_ENTRYRIGHT = 0x00
    LCD_ENTRYLEFT = 0x02
    LCD_ENTRYSHIFTINCREMENT = 0x01
    LCD_ENTRYSHIFTDECREMENT = 0x00

    # flags for display on/off control
    LCD_DISPLAYON = 0x04
    LCD_DISPLAYOFF = 0x00
    LCD_CURSORON = 0x02
    LCD_CURSOROFF = 0x00
    LCD_BLINKON = 0x01
    LCD_BLINKOFF = 0x00

    # flags for display/cursor shift
    LCD_DISPLAYMOVE = 0x08
    LCD_CURSORMOVE = 0x00

    # flags for display/cursor shift
    LCD_DISPLAYMOVE = 0x08
    LCD_CURSORMOVE = 0x00
    LCD_MOVERIGHT = 0x04
    LCD_MOVELEFT = 0x00

    # flags for function set
    LCD_8BITMODE = 0x10
    LCD_4BITMODE = 0x00
    LCD_2LINE = 0x08
    LCD_1LINE = 0x00
    LCD_5x10DOTS = 0x04
    LCD_5x8DOTS = 0x00

    def __init__(self, pin_rs=165, pin_e=164, pins_db=[163, 162, 161, 160]):
        self.pin_rs = pin_rs
        self.pin_e = pin_e
        self.pins_db = pins_db

        Controller.available_pins = [pin_rs, pin_e] + pins_db
        pin_controllers = {}
        for pin in Controller.available_pins:
            pin_controllers[pin] = Controller.alloc_pin(pin, OUTPUT)
        self.pin_controllers = pin_controllers

        self.write4bits(0x33)  # initialization
        self.write4bits(0x32)  # initialization
        self.write4bits(0x28)  # 2 line 5x7 matrix
        self.write4bits(0x0C)  # turn cursor off 0x0E to enable cursor
        self.write4bits(0x06)  # shift cursor right

        self.displaycontrol = self.LCD_DISPLAYON | self.LCD_CURSOROFF | self.LCD_BLINKOFF
        self.displayfunction = self.LCD_4BITMODE | self.LCD_1LINE | self.LCD_5x8DOTS
        self.displayfunction |= self.LCD_2LINE

        # Initialize to default text direction (for romance languages)
        self.displaymode = self.LCD_ENTRYLEFT | self.LCD_ENTRYSHIFTDECREMENT
        self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)  # set the entry mode
        self.clear()

    def begin(self, cols, lines):
        if (lines > 1):
            self.numlines = lines
            self.displayfunction |= self.LCD_2LINE
            self.currline = 0

    def home(self):
        self.write4bits(self.LCD_RETURNHOME)  # set cursor position to zero
        self.delayMicroseconds(3000)  # this command takes a long time!

    def clear(self):
        self.write4bits(self.LCD_CLEARDISPLAY)  # command to clear display
        self.delayMicroseconds(3000)  # 3000 microsecond sleep, clearing the display takes a long time

    def set_cursor(self, col, row):
        self.row_offsets = [0x00, 0x40, 0x14, 0x54]
        if row > self.numlines:
            row = self.numlines - 1  # we count rows starting w/0
        self.write4bits(self.LCD_SETDDRAMADDR | (col + self.row_offsets[row]))

    def display_off(self):
        """ Turn the display off (quickly) """
        self.displaycontrol &= ~self.LCD_DISPLAYON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def display_on(self):
        """ Turn the display on (quickly) """
        self.displaycontrol |= self.LCD_DISPLAYON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def corsor_off(self):
        """ Turns the underline cursor on/off """
        self.displaycontrol &= ~self.LCD_CURSORON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def cursor_on(self):
        """ Cursor On """
        self.displaycontrol |= self.LCD_CURSORON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def blink_off(self):
        """ Turn on and off the blinking cursor """
        self.displaycontrol &= ~self.LCD_BLINKON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def scroll_left(self):
        """ These commands scroll the display without changing the RAM """
        self.write4bits(self.LCD_CURSORSHIFT | self.LCD_DISPLAYMOVE | self.LCD_MOVELEFT)

    def scroll_right(self):
        """ These commands scroll the display without changing the RAM """
        self.write4bits(self.LCD_CURSORSHIFT | self.LCD_DISPLAYMOVE | self.LCD_MOVERIGHT)

    def left_to_right(self):
        """ This is for text that flows Left to Right """
        self.displaymode |= self.LCD_ENTRYLEFT
        self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)

    def right_to_left(self):
        """ This is for text that flows Right to Left """
        self.displaymode &= ~self.LCD_ENTRYLEFT
        self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)

    def autoscroll_on(self):
        """ This will 'right justify' text from the cursor """
        self.displaymode |= self.LCD_ENTRYSHIFTINCREMENT
        self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)

    def autoscroll_off(self):
        """ This will 'left justify' text from the cursor """
        self.displaymode &= ~self.LCD_ENTRYSHIFTINCREMENT
        self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)

    def write4bits(self, bits, char_mode=False):
        """ Send command to LCD """
        self.delayMicroseconds(1000)  # 1000 microsecond sleep
        bits = bin(bits)[2:].zfill(8)
        if char_mode:
            self.pin_controllers[self.pin_rs].set()
        else:
            self.pin_controllers[self.pin_rs].reset()

        for pin in self.pins_db:
            self.pin_controllers[pin].reset()
        for i in range(4):
            if bits[i] == "1":
                pin = self.pins_db[::-1][i]
                self.pin_controllers[pin].set()
        self.pulse_enable()

        for pin in self.pins_db:
            self.pin_controllers[pin].reset()

        for i in range(4, 8):
            if bits[i] == "1":
                pin = self.pins_db[::-1][i-4]
                self.pin_controllers[pin].set()
        self.pulse_enable()

    def delayMicroseconds(self, microseconds):
        seconds = microseconds / float(1000000)  # divide microseconds by 1 million for seconds
        sleep(seconds)

    def pulse_enable(self):
        self.pin_controllers[self.pin_e].reset()
        self.delayMicroseconds(1)  # 1 microsecond pause - enable pulse must be > 450ns
        self.pin_controllers[self.pin_e].set()
        self.delayMicroseconds(1)  # 1 microsecond pause - enable pulse must be > 450ns
        self.pin_controllers[self.pin_e].reset()
        self.delayMicroseconds(1)  # commands need > 37us to settle

    def message(self, text):
        """ Send string to LCD. Newline wraps to second line"""
        for char in text:
            if char == '\n':
                self.write4bits(0xC0)  # next line
            else:
                self.write4bits(ord(char), True)


def loop():
    lcd = CharLCD()
    while True:
        lcd.clear()
        sleep(2)
        lcd.message(" TEST MODE !\n Whatup?")
        sleep(10)

    return lcd


if __name__ == '__main__':
    try:
        lcd = loop()
        reactor.run()
    except:
        for pin in Controller.available_pins:
            Controller.dealloc_pin(pin)
        reactor.stop()
