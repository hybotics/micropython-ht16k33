HT16K33_BLINK_CMD = const(0x80)
HT16K33_BLINK_DISPLAYON = const(0x01)
HT16K33_CMD_BRIGHTNESS = const(0xE0)
HT16K33_OSCILATOR_ON = const(0x21)


class Matrix:
    def __init__(self, i2c, address=0x70):
        self.i2c = i2c
        self.address = address
        self.temp = bytearray(1)
        self.buffer = bytearray(16)
        self.fill(0)
        self.write_cmd(HT16K33_OSCILATOR_ON)
        self.blink_rate(0)
        self.brightness(15)

    def write_cmd(self, byte):
        self.temp[0] = byte
        self.i2c.writeto(self.address, self.temp)

    def blink_rate(self, rate=None):
        if rate is None:
            return self._blink_rate
        rate = rate & 0x02
        self._blink_rate = rate
        self.write_cmd(HT16K33_BLINK_CMD | HT16K33_BLINK_DISPLAYON | rate << 1)

    def brightness(self, brightness):
        if brightness is None:
            return self._brightness
        brightness = brightness & 0x0F
        self._brightness = brightness
        self.write_cmd(HT16K33_CMD_BRIGHTNESS | brightness)

    def show(self):
        self.i2c.writeto_mem(self.address, 0x00, self.buffer)

    def fill(self, color):
        fill = 0xff if color else 0x00
        for i in range(16):
            self.buffer[i] = fill

    def pixel(self, x, y, color=None):
        mask = 1 << x
        if color is None:
            return bool((self.buffer[y] | self.buffer[y + 1] << 8) & mask)
        if color:
            self.buffer[y * 2] |= mask & 0xff
            self.buffer[y * 2 + 1] |= mask >> 8
        else:
            self.buffer[y * 2] &= ~(mask & 0xff)
            self.buffer[y * 2 + 1] &= ~(mask >> 8)


class Matrix8x16(Matrix):
    def pixel(self, x, y, color=None):
        if not 0 <= x <= 15:
            return
        if not 0 <= y <= 8:
            return
        return super().pixel(x, y, color)


class Matrix8x8(Matrix):
    def pixel(self, x, y, color=None):
        if not 0 <= x <= 8:
            return
        if not 0 <= y <= 8:
            return
        x = (x - 1) % 8
        return super().pixel(x, y, color)
