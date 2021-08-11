"""
Docstring
"""
from utime import sleep
from micropython import const
from hybotics_ht16k33.segments import Seg14x4


class MultiSeg14x4(Seg14x4):
    """Docstring"""

    _DEFAULT_DISPLAY_BRIGHTNESS = 0.1

    def __init__(
        self,
        i2c,
        address,
        auto_write=False,
        brightness=_DEFAULT_DISPLAY_BRIGHTNESS,
        blink_rate=0,
    ):
        self._address = address
        self._auto_write = auto_write
        self._brightness = brightness
        self._blink_rate = blink_rate
        self._devices = []

        if isinstance(self._address, int):
            print("DEBUG: (multisegments.py) single display")
            self._devices = Seg14x4(i2c, self._address, auto_write, brightness)
        elif isinstance(self._address, list):
            print("DEBUG: (multisegments.py) multi-display")

            for index, addr in enumerate(self._address):
                print(
                    "DEBUG (multisegments.py) display {0} at self._address = {1}".format(
                        index, hex(addr)
                    )
                )

                self.devices.append(Seg14x4(i2c, addr, auto_write, brightness))
                self.devices[index]._address = addr
                self.devices[index]._brightness = brightness
                self.devices[index]._blink_rate = blink_rate

            self._NUMBER_OF_DISPLAYS = const(len(self.devices))
            self._NUMBER_OF_DIGITS = const(self._NUMBER_OF_DISPLAYS * 4)
            print(
                "DEBUG (multisegments.py) There are {0} displays".format(
                    len(self.devices)
                )
            )

    def clear(self, show=True):
        for nr, _ in enumerate(self._address):
            self.devices[nr].fill(0)

        if show:
            self.devices[nr].show()

    def fill(self, color):
        """Fill the whole display with a given color."""
        for _, disp in enumerate(self.devices):
            disp.fill(color)

        if self._auto_write:
            self.show()

    def show(self):
        """Light up all the displays"""
        for _, disp in enumerate(self.devices):
            disp.show()

    def print(self, value, decimal=0):
        """Print the value to the display."""
        if isinstance(value, (str)):
            self._multi_text(value)
        elif isinstance(value, (int, float)):
            self._number(value, decimal)
        else:
            raise ValueError("Unsupported display value type: {}".format(type(value)))
        if self._auto_write:
            self.show()

    def _multi_text(self, text, show=True, scroll=False):
        """Docstring"""
        length = len(text)

        if length > self._NUMBER_OF_DIGITS:
            if scroll:
                pass
            else:
                raise ValueError(
                    "Input overflow - '{0}' is too long for the display!".format(text)
                )

        if length > self._NUMBER_OF_DIGITS:
            # Also could choose to scroll the text instead of raising an error
            raise ValueError(
                "The text, '{0}', is too long for the display!".format(text)
            )

        self.clear(self._devices)

        for nr, _ in enumerate(self._address):
            self._devices[nr].print(text[length - (nr + 1) * 4 : length - (nr * 4)])

        self._devices[len(self._address) - 1].print(
            text[0 : length - int(length / 4) * 4]
        )

        if show:
            for nr, _ in enumerate(self._address):
                self._devices[nr].show()

    def multi_scroll(self, text, wait=1, show=True, loop=False):
        """Scroll the specified text to the display, with optional looping."""

        """
        Initialize
        """
        length = len(text)

        char_nr = 0
        disp_index = 0
        disp_nr = 0
        disp_pos = 0
        digits_per_display = 4
        shifting = False

        disp_shift = []

        for _, _ in enumerate(self._address):
            disp_shift.append(0)

        """
        Starting up
        """
        print()

        print("Starting up")
        while char_nr < length and disp_index < self._NUMBER_OF_DISPLAYS:
            print(
                "DEBUG(1) disp_nr = {0}, char_nr = {1}, disp_pos = {2}, _NUMBER_OF_DISPLAYS = {3}, length = {4}".format(
                    disp_nr, char_nr, disp_pos, self._NUMBER_OF_DISPLAYS, length
                )
            )

            if not shifting:
                print("Initializing displays for shifting")
                print(
                    "DEBUG(2) disp_nr = {0}, disp_pos = {1}, char = '{2}'".format(
                        disp_nr, disp_pos, text[char_nr]
                    )
                )

                self._devices[disp_nr].print(text[char_nr])

                if disp_pos == 3:
                    disp_pos = 0

                    if disp_nr < self._NUMBER_OF_DISPLAYS:
                        print(
                            "DEBUG(3) Resetting display position and incrementing display"
                        )

                        disp_nr += 1
                else:
                    disp_pos += 1

                char_nr += 1
                sleep(wait)

            nr_shifts = char_nr // digits_per_display
            shifting = nr_shifts > 0
            disp_nr = nr_shifts

            """
            Entering into the shifty state - everything has to be shifted to
            the left now.
            """
            print()

            while shifting and disp_nr > 0 and char_nr < length:
                print("Inside the shifty state")

                print(
                    "DEBUG(4) disp_nr = {0}, char = '{1}', disp_shift = {2}, disp_pos = {3}".format(
                        disp_nr, text[char_nr], disp_shift, disp_pos
                    )
                )

                """
                Do all the shifting
                """
                while disp_nr > 0 and char_nr < length:
                    if disp_pos == 3:
                        disp_pos = 0

                    print(
                        "Shifting for display {0}, disp_shift = {1}".format(
                            disp_nr, disp_shift
                        )
                    )

                    print(
                        "    Shifting character '{0}' to the left on display {1}".format(
                            text[disp_shift[disp_nr]], disp_nr
                        )
                    )

                    self._devices[disp_nr].print(text[disp_shift[disp_nr]])
                    disp_shift[disp_nr] += 1

                    print(
                        "DEBUG(5) disp_pos = {0}, char_nr = {1},  disp_nr = {2}".format(
                            disp_pos, char_nr, disp_nr
                        )
                    )

                    if disp_nr < 2:
                        print(
                            "    Adding new character '{0}' to display 0".format(
                                text[char_nr]
                            )
                        )

                        self._devices[0].print(text[char_nr])
                        char_nr += 1
                        disp_pos += 1

                    disp_nr -= 1

                    print()

                    sleep(wait)

        if show:
            for nr, _ in enumerate(self._address):
                self._devices[nr].show()

        sleep(2)

    def _number(self, number, decimal=0):
        """
		Display a floating point or integer number on the Adafruit HT16K33 based displays

		param: number int or float - The floating point or integer number to be displayed, which must be
			in the range 0 (zero) to 9999 for integers and floating point or integer numbers
			and between 0.0 and 999.0 or 99.00 or 9.000 for floating point numbers.
		param: decimal int - The number of decimal places for a floating point number if decimal
			is greater than zero, or the input number is an integer if decimal is zero.

        Returns: The output text string to be displayed.
        """

        auto_write = self._auto_write
        self._auto_write = False
        stnum = str(number)
        dot = stnum.find(".")

        if len(stnum) > self._NUMBER_OF_DIGITS + 1 or (
            (len(stnum) > self._NUMBER_OF_DIGITS) and (dot < 0)
        ):
            raise ValueError(
                "Input overflow - {0} is too long for the display!".format(number)
            )

        if dot < 0:
            # No decimal point (Integer)
            places = len(stnum)
        else:
            places = len(stnum[:dot])

        if places <= 0 < decimal:
            self.fill(False)
            places = 4

            if "." in stnum:
                places += 1

        # Set decimal places, if number of decimal places is specified (decimal > 0)
        if places > 0 < decimal < len(stnum[places:]) and dot > 0:
            txt = stnum[: dot + decimal + 1]
        elif places > 0:
            txt = stnum[:places]

        if len(txt) > self._NUMBER_OF_DIGITS + 1:
            raise ValueError(
                "Input overflow - {0} is too long for the display!".format(txt)
            )

        self._multi_text(txt)
        self._auto_write = auto_write

        return txt

    @property
    def blink_rate(self):
        """Return the blink rate."""
        return self._blink_rate

    @blink_rate.setter
    def blink_rate(self, blink_rate):
        """Set the blink rate. Range 0 - 3"""
        self._blink_rate = blink_rate

    @property
    def nr_disp(self):
        """The number of displays"""
        return self._NUMBER_OF_DISPLAYS

    @property
    def nr_digits(self):
        """The number of displays"""
        return self._NUMBER_OF_DIGITS
