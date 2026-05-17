"""
WS2812B NeoPixel control for the 8x8 chessboard LED grid.

Physical layout: LED 0 is a1 (bottom-left from White's side).
Rows increment upward (rank), columns increment rightward (file).
Square (file, rank) → LED index: rank * 8 + file  (0-indexed)

On Raspberry Pi, rpi-ws281x must be installed and the script run as root
(or with sudo) for DMA access. GPIO pin 18 (PWM0) is the data line.
"""

try:
    from rpi_ws281x import PixelStrip, Color
    _HARDWARE = True
except ImportError:
    _HARDWARE = False

LED_COUNT = 64
LED_PIN = 18       # GPIO18 / PWM0
LED_FREQ_HZ = 800_000
LED_DMA = 10
LED_BRIGHTNESS = 80   # 0-255; keep modest to avoid current draw issues
LED_INVERT = False
LED_CHANNEL = 0

# Colors (R, G, B)
OFF         = (0, 0, 0)
FROM_COLOR  = (200, 160, 0)    # amber — "from" square
TO_COLOR    = (0, 200, 80)     # green — "to" square
HINT_COLOR  = (0, 100, 220)    # blue — computer's move
CHECK_COLOR = (220, 0, 0)      # red — king in check
COL_PREVIEW = (60, 60, 60)     # dim white — column preview while selecting


def _square_index(file: int, rank: int) -> int:
    """file and rank are 0-indexed (0=a/1, 7=h/8)."""
    return rank * 8 + file


def _chess_square_index(square_name: str) -> int:
    """Convert UCI square name like 'e2' to LED index."""
    file = ord(square_name[0]) - ord('a')
    rank = int(square_name[1]) - 1
    return _square_index(file, rank)


class BoardLEDs:
    def __init__(self):
        if _HARDWARE:
            self._strip = PixelStrip(
                LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA,
                LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL
            )
            self._strip.begin()
        else:
            self._strip = None
        self._state = [OFF] * LED_COUNT

    def _set(self, idx: int, color: tuple):
        self._state[idx] = color
        if self._HARDWARE_strip():
            self._strip[idx] = Color(*color)

    def _HARDWARE_strip(self):
        return self._strip is not None

    def show(self):
        if self._HARDWARE_strip():
            self._strip.show()
        else:
            self._debug_print()

    def clear(self):
        self._state = [OFF] * LED_COUNT
        if self._HARDWARE_strip():
            for i in range(LED_COUNT):
                self._strip[i] = Color(0, 0, 0)
            self._strip.show()

    def highlight_move(self, from_sq: str, to_sq: str, color_from=FROM_COLOR, color_to=TO_COLOR):
        """Light the from and to squares for a move (e.g. 'e2', 'e4')."""
        self.clear()
        self._set(_chess_square_index(from_sq), color_from)
        self._set(_chess_square_index(to_sq), color_to)
        self.show()

    def highlight_column(self, file: int):
        """Dim-highlight an entire column (0-indexed) as a selection preview."""
        self.clear()
        for rank in range(8):
            self._set(_square_index(file, rank), COL_PREVIEW)
        self.show()

    def highlight_square(self, file: int, rank: int, color=FROM_COLOR):
        """Light a single square (0-indexed file/rank)."""
        self.clear()
        self._set(_square_index(file, rank), color)
        self.show()

    def highlight_check(self, king_sq: str):
        self._set(_chess_square_index(king_sq), CHECK_COLOR)
        self.show()

    def _debug_print(self):
        """Text representation for development without hardware."""
        files = "abcdefgh"
        lines = []
        for rank in range(7, -1, -1):
            row = []
            for file in range(8):
                color = self._state[_square_index(file, rank)]
                if color == OFF:
                    row.append(".")
                elif color == FROM_COLOR:
                    row.append("F")
                elif color == TO_COLOR:
                    row.append("T")
                elif color == HINT_COLOR:
                    row.append("H")
                elif color == CHECK_COLOR:
                    row.append("!")
                else:
                    row.append("*")
            lines.append(f"{rank+1} " + " ".join(row))
        lines.append("  " + " ".join(files))
        print("\n".join(lines))
