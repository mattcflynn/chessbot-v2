"""
Button-pair input for square selection.

Physical layout: 8 column buttons (a-h) along one board edge,
8 row buttons (1-8) along an adjacent edge. Player presses col then row
to select a square; one selection = "from", second = "to".

On Raspberry Pi: RPi.GPIO handles button polling with pull-up resistors.
Off-Pi: falls back to keyboard input for development.

GPIO pin mapping (adjust to match physical wiring):
  COL_PINS[0..7] → buttons for columns a-h
  ROW_PINS[0..7] → buttons for rows 1-8
"""

try:
    import RPi.GPIO as GPIO
    _HARDWARE = True
except ImportError:
    _HARDWARE = False

import time

COL_PINS = [4, 5, 6, 7, 8, 9, 10, 11]    # GPIO pins for columns a-h
ROW_PINS = [12, 13, 14, 15, 16, 17, 20, 21]  # GPIO pins for rows 1-8

DEBOUNCE_MS = 50


def _setup_gpio():
    GPIO.setmode(GPIO.BCM)
    for pin in COL_PINS + ROW_PINS:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def _wait_for_button(pins: list[int]) -> int:
    """Block until one of the given pins goes LOW. Returns the index pressed."""
    while True:
        for i, pin in enumerate(pins):
            if GPIO.input(pin) == GPIO.LOW:
                time.sleep(DEBOUNCE_MS / 1000)
                if GPIO.input(pin) == GPIO.LOW:
                    while GPIO.input(pin) == GPIO.LOW:
                        pass
                    return i
        time.sleep(0.01)


def _read_square_hardware() -> tuple[int, int]:
    """Returns (file, rank) both 0-indexed."""
    file = _wait_for_button(COL_PINS)
    rank = _wait_for_button(ROW_PINS)
    return file, rank


def _read_square_keyboard(prompt: str) -> tuple[int, int]:
    """Fallback for dev — accepts algebraic input like 'e2'."""
    files = "abcdefgh"
    while True:
        raw = input(prompt).strip().lower()
        if len(raw) == 2 and raw[0] in files and raw[1] in "12345678":
            return files.index(raw[0]), int(raw[1]) - 1
        print("Enter a square like e2")


class BoardInput:
    def __init__(self):
        if _HARDWARE:
            _setup_gpio()

    def read_move(self, on_col_selected=None, on_from_selected=None) -> tuple[str, str]:
        """
        Prompts for a two-square move. Returns (from_sq, to_sq) as UCI strings, e.g. ('e2', 'e4').

        Callbacks (called with file, rank args, both 0-indexed):
          on_col_selected   — called after player picks a column (for LED column preview)
          on_from_selected  — called after from-square is confirmed (for LED from-highlight)
        """
        files = "abcdefgh"

        from_sq = self._read_one_square(
            "from",
            on_col_selected=on_col_selected,
            on_square_confirmed=on_from_selected,
        )
        to_sq = self._read_one_square("to")
        return from_sq, to_sq

    def _read_one_square(self, label: str, on_col_selected=None, on_square_confirmed=None) -> str:
        files = "abcdefgh"
        while True:
            if _HARDWARE:
                file, rank = _read_square_hardware()
            else:
                file, rank = _read_square_keyboard(f"  Select {label} square: ")

            if on_col_selected:
                on_col_selected(file, rank)

            # On hardware, col and row are separate button presses; on keyboard they arrive together.
            # The column preview callback fires after col is pressed but before row is pressed.
            # Since keyboard mode returns both at once, the preview is a no-op in that case.

            sq = f"{files[file]}{rank + 1}"
            if on_square_confirmed:
                on_square_confirmed(file, rank)
            return sq

    def cleanup(self):
        if _HARDWARE:
            GPIO.cleanup()
