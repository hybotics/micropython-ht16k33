from hybotics_ht16k33.ht16k33 import HT16K33

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
