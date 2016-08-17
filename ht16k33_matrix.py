_HT16K33_BLINK_CMD = const(0x80)
_HT16K33_BLINK_DISPLAYON = const(0x01)
_HT16K33_CMD_BRIGHTNESS = const(0xE0)
_HT16K33_OSCILATOR_ON = const(0x21)


class HT16K33:
    """The base class for all HT16K33-based backpacks and wings."""

    def __init__(self, i2c, address=0x70):
        self.i2c = i2c
        self.address = address
        self._temp = bytearray(1)
        self.buffer = bytearray(16)
        self.fill(0)
        self._write_cmd(_HT16K33_OSCILATOR_ON)
        self.blink_rate(0)
        self.brightness(15)

    def _write_cmd(self, byte):
        """Send a command."""
        self._temp[0] = byte
        self.i2c.writeto(self.address, self._temp)

    def blink_rate(self, rate=None):
        """Get or set the blink rate."""
        if rate is None:
            return self._blink_rate
        rate = rate & 0x02
        self._blink_rate = rate
        self._write_cmd(_HT16K33_BLINK_CMD |
                        _HT16K33_BLINK_DISPLAYON | rate << 1)

    def brightness(self, brightness):
        """Get or set the brightness (0-15)."""
        if brightness is None:
            return self._brightness
        brightness = brightness & 0x0F
        self._brightness = brightness
        self._write_cmd(_HT16K33_CMD_BRIGHTNESS | brightness)

    def show(self):
        """Actually send all the changes to the device."""
        self.i2c.writeto_mem(self.address, 0x00, self.buffer)

    def fill(self, color):
        """Fill the display with given color."""
        fill = 0xff if color else 0x00
        for i in range(16):
            self.buffer[i] = fill

    def _pixel(self, x, y, color=None):
        """Set a single pixel in the frame buffer to specified color."""
        mask = 1 << x
        if color is None:
            return bool((self.buffer[y] | self.buffer[y + 1] << 8) & mask)
        if color:
            self.buffer[y * 2] |= mask & 0xff
            self.buffer[y * 2 + 1] |= mask >> 8
        else:
            self.buffer[y * 2] &= ~(mask & 0xff)
            self.buffer[y * 2 + 1] &= ~(mask >> 8)


class Matrix16x8(HT16K33):
    """The double matrix."""

    def pixel(self, x, y, color=None):
        """Set a single pixel to specified color."""
        if not 0 <= x <= 15:
            return
        if not 0 <= y <= 7:
            return
        if x >= 8:
            x -= 8
            y += 8
        return super()._pixel(y, x, color)


class Matrix8x8(HT16K33):
    """The single matrix."""

    def pixel(self, x, y, color=None):
        """Set a single pixel to specified color."""
        if not 0 <= x <= 7:
            return
        if not 0 <= y <= 7:
            return
        x = (x - 1) % 8
        return super()._pixel(x, y, color)


class Matrix8x8x2(HT16K33):
    """The bi-color matrix."""

    def pixel(self, x, y, color=None):
        """Set a single pixel to specified color."""
        if not 0 <= x <= 7:
            return
        if not 0 <= y <= 7:
            return
        if color is not None:
            super()._pixel(y, x, (color & 0x01))
            super()._pixel(y + 8, x, (color >> 1) & 0x01)
        else:
            return super()._pixel(y, x) | super()._pixel(y + 8, x) << 1

    def fill(self, color):
        """Fill the display with given color."""
        fill1 = 0xff if color & 0x01 else 0x00
        fill2 = 0xff if color & 0x02 else 0x00
        for i in range(8):
            self.buffer[i * 2] = fill1
            self.buffer[i * 2 + 1] = fill2
