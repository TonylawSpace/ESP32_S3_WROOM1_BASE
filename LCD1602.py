# LCD1602.py
# -*- coding: utf-8 -*-
import time
from machine import Pin, I2C

# Define SDA and SCL pins for I2C communication
I2C_SDA = Pin(4)
I2C_SCL = Pin(5)

# Initialize I2C with frequency 400kHz
I2C = I2C(0, sda=I2C_SDA, scl=I2C_SCL, freq=400000)

# LCD1602 LCD commands and addresses
LCD_ADDRESS = (0x7c >> 1)  # LCD I2C address

# LCD control command constants
LCD_CLEARDISPLAY = 0x01  # Clear display command
LCD_RETURNHOME = 0x02  # Return to home position command
LCD_ENTRYMODESET = 0x04  # Entry mode set command
LCD_DISPLAYCONTROL = 0x08  # Display control command
LCD_CURSORSHIFT = 0x10  # Cursor shift command
LCD_FUNCTIONSET = 0x20  # Function set command
LCD_SETCGRAMADDR = 0x40  # Set CGRAM address command
LCD_SETDDRAMADDR = 0x80  # Set DDRAM address command

# Flags for entry mode (text direction)
LCD_ENTRYRIGHT = 0x00
LCD_ENTRYLEFT = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00

# Flags for display on/off control
LCD_DISPLAYON = 0x04
LCD_DISPLAYOFF = 0x00
LCD_CURSORON = 0x02
LCD_CURSOROFF = 0x00
LCD_BLINKON = 0x01
LCD_BLINKOFF = 0x00

# Flags for display and cursor shift
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE = 0x00
LCD_MOVERIGHT = 0x04
LCD_MOVELEFT = 0x00

# Flags for function set (data length, number of lines, etc.)
LCD_8BITMODE = 0x10
LCD_4BITMODE = 0x00
LCD_2LINE = 0x08
LCD_1LINE = 0x00
LCD_5x8DOTS = 0x00

class LCD1602:
    def __init__(self, col, row):
        self._row = row
        self._col = col

        # Set the display function (4-bit mode, 1-line, 5x8 font)
        self._showfunction = LCD_4BITMODE | LCD_1LINE | LCD_5x8DOTS
        self.begin(self._row, self._col)

    # Send command to the LCD
    def command(self, cmd):
        I2C.writeto_mem(LCD_ADDRESS, 0x80, bytearray([cmd]))

    # Send data to the LCD
    def data(self, data):
        I2C.writeto_mem(LCD_ADDRESS, 0x40, bytearray([data]))

    # Set the cursor position
    def setCursor(self, col, row):
        if row == 0:
            col |= 0x80  # Set address for the first row
        else:
            col |= 0xc0  # Set address for the second row
        self.command(col)

    # Clear the LCD display
    def clear(self):
        self.command(LCD_CLEARDISPLAY)  # Send clear command
        time.sleep(0.005)  # Wait for the command to execute

    # Print a string or number to the display
    def printout(self, arg):
        if isinstance(arg, int):
            arg = str(arg)  # Convert integer to string
        for x in bytearray(arg, 'utf-8'):  # Send each character to LCD
            self.data(x)

    # Create a custom character at a specified location
    def createChar(self, location, charmap):
        location = location & 0x7  # Ensure location is within bounds (0-7)
        self.command(LCD_SETCGRAMADDR | (location << 3))  # Set CGRAM address
        for i in range(0, 8):
            self.data(charmap[i])  # Write the character map data to CGRAM

    # Scroll the display left
    def scrollDisplayLeft(self):
        self.command(LCD_CURSORSHIFT | LCD_DISPLAYMOVE | LCD_MOVELEFT)

    # Scroll the display right
    def scrollDisplayRight(self):
        self.command(LCD_CURSORSHIFT | LCD_DISPLAYMOVE | LCD_MOVERIGHT)

    # Turn on the underline cursor
    def cursor(self):
        self._showcontrol |= LCD_CURSORON
        self.command(LCD_DISPLAYCONTROL | self._showcontrol)

    # Turn off the underline cursor
    def nocursor(self):
        self._showcontrol &= ~LCD_CURSORON
        self.command(LCD_DISPLAYCONTROL | self._showcontrol)

    # Set text direction from left to right
    def leftToRight(self):
        self._showmode |= LCD_ENTRYLEFT
        self.command(LCD_ENTRYMODESET | self._showmode)

    # Set text direction from right to left
    def rightToLeft(self):
        self._showmode &= ~LCD_ENTRYLEFT
        self.command(LCD_ENTRYMODESET | self._showmode)

    # Enable auto-scroll
    def autoscroll(self):
        self._showmode |= LCD_ENTRYSHIFTINCREMENT
        self.command(LCD_ENTRYMODESET | self._showmode)

    # Disable auto-scroll
    def noautoscroll(self):
        self._showmode &= ~LCD_ENTRYSHIFTINCREMENT
        self.command(LCD_ENTRYMODESET | self._showmode)

    # Turn on the display
    def display(self):
        self._showcontrol |= LCD_DISPLAYON
        self.command(LCD_DISPLAYCONTROL | self._showcontrol)

    # Initialize the LCD (send necessary commands for configuration)
    def begin(self, cols, lines):
        if lines > 1:
            self._showfunction |= LCD_2LINE  # Enable 2-line display
        self._numlines = lines
        self._currline = 0
        time.sleep(0.05)

        # Send function set command sequence
        self.command(LCD_FUNCTIONSET | self._showfunction)
        time.sleep(0.005)
        self.command(LCD_FUNCTIONSET | self._showfunction)
        time.sleep(0.005)
        self.command(LCD_FUNCTIONSET | self._showfunction)
        self.command(LCD_FUNCTIONSET | self._showfunction)

        # Turn on display with no cursor or blinking
        self._showcontrol = LCD_DISPLAYON | LCD_CURSOROFF | LCD_BLINKOFF
        self.display()

        # Clear the screen
        self.clear()

        # Set entry mode for text direction (left to right)
        self._showmode = LCD_ENTRYLEFT | LCD_ENTRYSHIFTDECREMENT
        self.command(LCD_ENTRYMODESET | self._showmode)
