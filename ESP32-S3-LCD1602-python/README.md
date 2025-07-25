# Waveshare LCD1602 I2C Module

- [中文版](./README_CN.md)

If you're used to traditional LCD1602 displays, try out the I2C communication version of the LCD1602. Compared to the traditional version, it occupies fewer pins and is easier to operate.

# Product Link(https://www.waveshare.com/lcd1602-i2c-module.htm)

    SKU：23991

# Directory Overview
* examples: Example source code files
* lib: LCD1602 driver files
* bin: Micropython firmware for ESP32S3

# Overview

The Waveshare LCD1602 I2C Module features an LCD screen with various backlight colors and can display 2x16 characters. It supports screen scrolling, cursor movement, backlight brightness adjustment, and more.

# Hardware connection
LCD1602 	-> ESP32S3

VCC 	-> 3V3
GND  	-> GND
SCL 	-> GP5
SDA 	-> GP4

# Driver Installation

Before using this library, first navigate to the uf2 folder and flash the appropriate Micropython firmware for your RP2040. Then, download the library files and place the .py files from the lib folder onto the RP2040. Afterward, open the examples folder and run the demonstrations inside that folder.

# Function Descriptions

```MicroPython
  def command(self, cmd)
    '''
      @brief send command
      @param cmd The command to send
    '''
    
  def data(self, data)
    '''
      @brief Write a character
      @param data Data to be written
    '''

  def setCursor(self, col, row)
    '''
      @brief Set cursor position
      @param col Column number (0-39)
      @param row Row number (0-1), where 0 represents the first row, and 1 represents the second row
    '''

  def clear(self)
    '''
      @brief Clear the display and return the cursor to the initial position (0 position)
    '''

  def printout(self, arg)
    '''
      @brief Output data to the LCD screen
      @param arg Data to be displayed
    '''

  def createChar(self, location, charmap)
    '''
      @brief Allows us to fill the first 8 CGRAM locations with custom characters
      @param location Character location (range 0-7)
      @param charmap Character data (array of 8 bytes)
    '''

  def scrollDisplayLeft(self)
    '''
      @brief Scroll the display to the left
    '''

  def scrollDisplayRight(self)
    '''
      @brief Scroll the display to the right
    '''

  def cursor(self)
    '''
      @brief Enable the underscore cursor
    '''

  def nocursor(self)
    '''
      @brief Disable the underscore cursor
    '''

  def leftToRight(self)
    '''
      @brief Enable left-to-right text flow
    '''

  def rightToLeft(self)
    '''
      @brief Enable right-to-left text flow
    '''

  def autoscroll(self)
    '''
      @brief Enable right-aligned text from the cursor position
    '''

  def noautoscroll(self)
    '''
      @brief Enable left-aligned text from the cursor position
    '''

  def display(self)
    '''
      @brief Turn on the display
    '''

  def set_brightness(self, Value)
    '''
      @brief Set backlight brightness
      @param Value Brightness level (0-100)
    '''

  def set_mode(self, Mode)
    '''
      @brief Set backlight mode
      @param Mode Normal mode (0x00), Breathing mode (0x20)
    '''
```

## Compatibility

| Board     | Work Well | Work Wrong | Untested | Remarks |
| ---------	|  :-------:  | :-------: | :-------: | :-------: |
| ESP32S3 	|      √      |           |         	|         	|

## History

- Date 2025-01-06
- Version V1.0.0
