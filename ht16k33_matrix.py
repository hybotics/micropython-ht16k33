import framebuf

_HT16K33_BLINK_CMD = const(0x80)
_HT16K33_BLINK_DISPLAYON = const(0x01)
_HT16K33_CMD_BRIGHTNESS = const(0xE0)
_HT16K33_OSCILATOR_ON = const(0x21)


class HT16K33:
    def __init__(self, i2c, address=0x70):
        self.i2c = i2c
        self.address = address
        self._temp = bytearray(1)

        self._buffer = bytearray(self.WIDTH * self.HEIGHT // 4)
        self._fb_buffer = bytearray(self.WIDTH * self.HEIGHT * self.FB_BPP // 8)
        self.framebuffer = framebuf.FrameBuffer(
            self._fb_buffer, self.WIDTH, self.HEIGHT, self.FORMAT)

        self.framebuffer.fill(0)
        self._write_cmd(_HT16K33_OSCILATOR_ON)
        self.blink_rate(0)
        self.brightness(15)

        self.pixel = self.framebuffer.pixel
        self.fill = self.framebuffer.fill

    def _write_cmd(self, byte):
        self._temp[0] = byte
        self.i2c.writeto(self.address, self._temp)

    def blink_rate(self, rate=None):
        if rate is None:
            return self._blink_rate
        rate = rate & 0x03
        self._blink_rate = rate
        self._write_cmd(_HT16K33_BLINK_CMD |
                        _HT16K33_BLINK_DISPLAYON | rate << 1)

    def brightness(self, brightness):
        if brightness is None:
            return self._brightness
        brightness = brightness & 0x0F
        self._brightness = brightness
        self._write_cmd(_HT16K33_CMD_BRIGHTNESS | brightness)

    def show(self):
        """Actually send all the changes to the device."""
        self._copy_buf()
        self.i2c.writeto_mem(self.address, 0x00, self._buffer)


class Matrix16x8(HT16K33):
    """The double matrix."""
    WIDTH = 16
    HEIGHT = 8
    FORMAT = framebuf.MONO_HLSB
    FB_BPP = 1

    def _copy_buf(self):
        for y in range(8):
            b = self._fb_buffer[y]
            self._buffer[y * 2] = b


class Matrix8x8(HT16K33):
    """The single matrix."""
    WIDTH = 8
    HEIGHT = 8
    FORMAT = framebuf.MONO_HLSB
    FB_BPP = 1

    def _copy_buf(self):
        for y in range(8):
            b = self._fb_buffer[y]
            self._buffer[y * 2] = (b >> 1) | (b << 7)


class Matrix8x8x2(HT16K33):
    """The bi-color matrix."""
    WIDTH = 8
    HEIGHT = 8
    FORMAT = framebuf.GS4_HMSB
    FB_BPP = 4

    def _copy_buf(self):
        pixel = self.framebuffer.pixel
        _buffer = self._buffer
        for y in range(8):
            b = 0
            for x in range(8):
                color = pixel(y, x)
                if color & 1:
                    b += 1 << x
                if color & 2:
                    b += 1 << x
            _buffer[y*2] = b & 0xff
            _buffer[y*2+1] = (b >> 8) & 0xff


class Matrix8x8x2Mini(HT16K33):
    """The D1 Mini bi-color shield."""
    WIDTH = 8
    HEIGHT = 8
    FORMAT = framebuf.GS4_HMSB
    FB_BPP = 4

    _ROWS1 = (1, 3, 5, 12, 14, 15, 13, 11)
    _ROWS2 = (9, 7, 0, 2, 4, 6, 8, 10)

    def _copy_buf(self):
        pixel = self.framebuffer.pixel
        _buffer = self._buffer
        _ROWS1 = self._ROWS1
        _ROWS2 = self._ROWS2
        for y in range(8):
            b = 0
            for x in range(8):
                color = pixel(y, x)
                if color & 1:
                    b += 1 << _ROWS1[x]
                if color & 2:
                    b += 1 << _ROWS2[x]
            _buffer[y*2] = b & 0xff
            _buffer[y*2+1] = (b >> 8) & 0xff
