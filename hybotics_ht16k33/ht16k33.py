# SPDX-FileCopyrightText: Radomir Dopieralski 2016 for Adafruit Industries
# SPDX-FileCopyrightText: Tony DiCola 2016 for Adafruit Industries
# SPDX-FileCopyrightText: Dale Weber 2021
#
# SPDX-License-Identifier: MIT

"""
`hybotics_ht16k33.ht16k33`
===========================

* Authors: Radomir Dopieralski & Tony DiCola for Adafruit Industries

* Ported to Micropython by Dale Weber <hybotics.wy@gmail.com>
"""

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/hybotics/Hybotics_Micropython_HT16K33.git"

from micropython import const
from utime import sleep

_HT16K33_BLINK_CMD = const(0x80)
_HT16K33_BLINK_DISPLAYON = const(0x01)
_HT16K33_CMD_BRIGHTNESS = const(0xE0)
_HT16K33_OSCILATOR_ON = const(0x21)

RETRY_MAX = 10
RETRY_WAIT_SEC = 1.0

class HT16K33:
    """The base class for all HT16K33-based backpacks and wings."""

    def __init__(self, i2c, address=0x70, auto_write=True, brightness=1.0):
        self.i2c = i2c
        self.address = address
        self._temp = bytearray(1)
        self._buffer = bytearray(17)
        self._auto_write = auto_write
        self.fill(0)
        self._write_cmd(_HT16K33_OSCILATOR_ON)
        self._blink_rate = None
        self._brightness = None
        self.blink_rate = 0
        self.brightness = brightness
        self.fill(0)

    def _write_cmd(self, byte):
        self._temp[0] = byte
        self.i2c.writeto(self.address, bytes(self._temp))

    @property
    def blink_rate(self):
        """The blink rate. Range 0-3."""
        return self._blink_rate

    @blink_rate.setter
    def blink_rate(self, rate=None):
        if not 0 <= rate <= 3:
            raise ValueError("Blink rate must be an integer in the range: 0-3")
        rate = rate & 0x03
        self._blink_rate = rate
        self._write_cmd(_HT16K33_BLINK_CMD | _HT16K33_BLINK_DISPLAYON | rate << 1)

    @property
    def brightness(self):
        """The brightness. Range 0.0-1.0"""
        return self._brightness

    @brightness.setter
    def brightness(self, brightness):
        if not 0.0 <= brightness <= 1.0:
            raise ValueError(
                "Brightness must be a decimal number in the range: 0.0-1.0"
            )

        self._brightness = brightness
        xbright = round(15 * brightness)
        xbright = xbright & 0x0F
        self._write_cmd(_HT16K33_CMD_BRIGHTNESS | xbright)

    @property
    def auto_write(self):
        """Auto write updates to the display."""
        return self._auto_write

    @auto_write.setter
    def auto_write(self, auto_write):
        if isinstance(auto_write, bool):
            self._auto_write = auto_write
        else:
            raise ValueError("Must set to either True or False.")

    def show(self):
        """Refresh the display and show the changes."""
        self.i2c.writeto(self.address, bytes(self._buffer))

    def fill(self, color):
        """Fill the whole display with the given color."""
        fill = 0xFF if color else 0x00
        for i in range(16):
            self._buffer[i + 1] = fill
        if self._auto_write:
            self.show()

    def _pixel(self, x, y, color=None):
        addr = 2 * y + x // 8
        mask = 1 << x % 8
        if color is None:
            return bool(self._buffer[addr + 1] & mask)
        if color:
            # set the bit
            self._buffer[addr + 1] |= mask
        else:
            # clear the bit
            self._buffer[addr + 1] &= ~mask
        if self._auto_write:
            self.show()
        return None

    def _set_buffer(self, i, value):
        self._buffer[i + 1] = value  # Offset by 1 to move past register address.

    def _get_buffer(self, i):
        return self._buffer[i + 1]  # Offset by 1 to move past register address.
