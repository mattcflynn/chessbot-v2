"""
Button input for the chess board.

Hardware layout (adjust pin numbers to match physical wiring):
  COL_PINS[0..7] → column buttons a-h (along one board edge)
  ROW_PINS[0..7] → row buttons 1-8 (along adjacent edge)
  SELECT_PIN     → confirm selection
  BACK_PIN       → cancel step (idle = open menu; mid-selection = go back)

All buttons: normally open, active LOW, internal pull-up enabled.
"""

try:
    import RPi.GPIO as GPIO
    _HARDWARE = True
except ImportError:
    _HARDWARE = False

import time

SELECT_PIN = 2    # GPIO2 — confirm / select
BACK_PIN   = 3    # GPIO3 — back one step / open menu from idle

COL_PINS = [4, 5, 6, 7, 19, 20, 26, 27]    # columns a-h
ROW_PINS = [12, 13, 14, 15, 16, 17, 21, 22] # rows 1-8

DEBOUNCE_MS = 50


def _setup_gpio():
    GPIO.setmode(GPIO.BCM)
    for pin in COL_PINS + ROW_PINS + [SELECT_PIN, BACK_PIN]:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def _is_pressed(pin: int) -> bool:
    return GPIO.input(pin) == GPIO.LOW


def _wait_release(pin: int):
    while _is_pressed(pin):
        time.sleep(0.005)


class ButtonReader:
    def __init__(self):
        if _HARDWARE:
            _setup_gpio()

    def wait_for_any(self) -> tuple[str, int]:
        """
        Blocks until a button is pressed.
        Returns one of:
          ('col', 0-7)   — column button a-h
          ('row', 0-7)   — row button 1-8
          ('select', 0)  — SELECT button
          ('back', 0)    — BACK/MENU button
        """
        if not _HARDWARE:
            return self._kb_any()

        tagged = (
            [(pin, 'col', i)    for i, pin in enumerate(COL_PINS)] +
            [(pin, 'row', i)    for i, pin in enumerate(ROW_PINS)] +
            [(SELECT_PIN, 'select', 0), (BACK_PIN, 'back', 0)]
        )
        while True:
            for pin, btn_type, idx in tagged:
                if _is_pressed(pin):
                    time.sleep(DEBOUNCE_MS / 1000)
                    if _is_pressed(pin):
                        _wait_release(pin)
                        return btn_type, idx
            time.sleep(0.01)

    def wait_for_row(self) -> int:
        """Blocks until a row button (1-8) is pressed. Returns 0-7 index."""
        if not _HARDWARE:
            while True:
                raw = input("Choose row 1-8: ").strip()
                if len(raw) == 1 and raw in "12345678":
                    return int(raw) - 1
            return
        while True:
            for i, pin in enumerate(ROW_PINS):
                if _is_pressed(pin):
                    time.sleep(DEBOUNCE_MS / 1000)
                    if _is_pressed(pin):
                        _wait_release(pin)
                        return i
            time.sleep(0.01)

    def _kb_any(self) -> tuple[str, int]:
        """Keyboard simulation for development — single-character input."""
        files = "abcdefgh"
        prompt = "col(a-h) row(1-8) select(Enter) back(x): "
        while True:
            raw = input(prompt).strip().lower()
            if not raw:
                return 'select', 0
            if raw == 'x':
                return 'back', 0
            if len(raw) == 1 and raw in files:
                return 'col', files.index(raw)
            if len(raw) == 1 and raw in "12345678":
                return 'row', int(raw) - 1
            # Shortcut: full move like e2e4 → return special token
            if len(raw) == 4:
                return 'move_shortcut', raw  # handled in game.py

    def cleanup(self):
        if _HARDWARE:
            GPIO.cleanup()
