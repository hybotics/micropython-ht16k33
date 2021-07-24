# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Basic example of setting digits on a LED segment display.
# This example and library is meant to work with Adafruit CircuitPython API.
# Author: Tony DiCola
# License: Public Domain
from micropython import const
from utime import sleep

# Import all board pins.
from machine import SoftI2C, Pin
# Import the HT16K33 LED segment module.
from hybotics_ht16k33.segments import Seg14x4
# Import special stuff for tinyPico
from tinypico import I2C_SDA, I2C_SCL

TP_SDA = Pin(I2C_SDA)
TP_SCL = Pin(I2C_SCL) 

DELAY_BETWEEN_SEC = 4

# Create the I2C interface.
i2c = SoftI2C(sda=TP_SDA, scl=TP_SCL, freq=400000)

# Create the LED segment class.
# This creates a 7 segment 4 character display:
display = Seg14x4(i2c)
# Or this creates a 14 segment alphanumeric 4 character display:
# display = segments.Seg14x4(i2c)
# Or this creates a big 7 segment 4 character display
# display = segments.BigSeg7x4(i2c)
# Finally you can optionally specify a custom I2C address of the HT16k33 like:
# display = segments.Seg7x4(i2c, address=0x70)

try:
  print()
  print("4 Digit, 14 Segment Alphanumeric Demo Starting Up - Ctrl/C to Exit")
  print()
  # Clear the display.
  # display.fill(0)
  sleep(DELAY_BETWEEN_SEC)

  # Can just print an integer number
  int_number = 6358
  print("Printing an integer number {0}".format(int_number))
  display.print(int_number)
  sleep(DELAY_BETWEEN_SEC)
  display.fill(0)

  # Can just print a floating point number
  float_number = 714.4
  print("Printing a floating point number {0}".format(float_number))
  display.print(float_number, 1)
  sleep(DELAY_BETWEEN_SEC)
  display.fill(0)

  # Or, can print a hexadecimal value
  hex_number = 0xBEAD
  print("Printing a hexadecimal number {0}".format(hex(hex_number)))
  display.print_hex(hex_number)
  sleep(DELAY_BETWEEN_SEC)
  display.fill(0)

  # Or, can set indivdual digits / characters
  # Set the first character to '1':
  display[0] = "1"
  # Set the second character to '2':
  display[1] = "2"
  # Set the third character to 'A':
  display[2] = "A"
  # Set the forth character to 'B':
  display[3] = "B"
  sleep(DELAY_BETWEEN_SEC)
  display.fill(0)

  # Or, can even set the segments to make up characters
  if isinstance(display, Seg14x4):
      # 14-segment raw digits
      display.set_digit_raw(0, 0x2D3F)
      display.set_digit_raw(1, 0b0010110100111111)
      display.set_digit_raw(2, (0b00101101, 0b00111111))
      display.set_digit_raw(3, [0x2D, 0x3F])
  else:
      # 7-segment raw digits
      display.set_digit_raw(0, 0xFF)
      display.set_digit_raw(1, 0b11111111)
      display.set_digit_raw(2, 0x79)
      display.set_digit_raw(3, 0b01111001)

  sleep(DELAY_BETWEEN_SEC)
  display.fill(0)

  # Show a looping marquee
  display.marquee("Deadbeef 192.168.100.102... ", 0.2)
except KeyboardInterrupt:
  # display.fill(0)
  led_green.value(False)
  led_yellow.value(False)
