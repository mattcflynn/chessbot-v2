"""
3.5" SPI TFT display driver using PIL for rendering.

On Raspberry Pi: install adafruit-circuitpython-rgb-display + adafruit-blinka.
Wiring (Waveshare 3.5" or Adafruit 3.5" TFT HAT — adjust pins to match your board):
  CS  → GPIO8  (CE0, hardware SPI)
  DC  → GPIO25
  RST → GPIO24
  BL  → GPIO7  (backlight, set HIGH to enable)

Off-Pi: prints state to terminal instead.
"""

try:
    import board
    import digitalio
    import adafruit_rgb_display.ili9341 as ili9341
    _HARDWARE = True
except ImportError:
    _HARDWARE = False

import chess
from PIL import Image, ImageDraw, ImageFont

SCREEN_W, SCREEN_H = 480, 320

BG_COLOR      = (20, 20, 30)
TEXT_COLOR    = (230, 230, 230)
ACCENT_COLOR  = (80, 200, 120)
WARNING_COLOR = (220, 80, 80)


def _make_font(size: int):
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    except OSError:
        return ImageFont.load_default()


class Display:
    def __init__(self):
        if _HARDWARE:
            import busio
            import adafruit_rgb_display.ili9341 as ili9341
            cs   = digitalio.DigitalInOut(board.CE0)
            dc   = digitalio.DigitalInOut(board.D25)
            rst  = digitalio.DigitalInOut(board.D24)
            spi  = busio.SPI(clock=board.SCK, MOSI=board.MOSI, MISO=board.MISO)
            self._tft = ili9341.ILI9341(spi, cs=cs, dc=dc, rst=rst, baudrate=24_000_000)
        else:
            self._tft = None

        self._font_large = _make_font(36)
        self._font_med   = _make_font(24)
        self._font_small = _make_font(18)

    def _render(self, img: Image.Image):
        if self._tft:
            self._tft.image(img)
        else:
            pass  # dev mode: no-op; callers print to terminal instead

    def show_game_state(self, turn: str, last_move: str | None, eval_cp: int | None, in_check: bool):
        img = Image.new("RGB", (SCREEN_W, SCREEN_H), BG_COLOR)
        d = ImageDraw.Draw(img)

        # Whose turn
        turn_color = ACCENT_COLOR if turn == "White" else WARNING_COLOR
        d.text((20, 20), f"{turn}'s turn", font=self._font_large, fill=turn_color)

        if in_check:
            d.text((20, 70), "CHECK!", font=self._font_large, fill=WARNING_COLOR)

        # Last computer move
        if last_move:
            d.text((20, 130), "Computer played:", font=self._font_small, fill=TEXT_COLOR)
            d.text((20, 155), last_move.upper(), font=self._font_large, fill=ACCENT_COLOR)

        # Eval bar
        if eval_cp is not None:
            label = f"Eval: {'+' if eval_cp >= 0 else ''}{eval_cp / 100:.1f}"
            d.text((20, 260), label, font=self._font_med, fill=TEXT_COLOR)

        self._render(img)

        if not self._tft:
            arrow = "→" if turn == "White" else "←"
            check = " CHECK!" if in_check else ""
            move_info = f"  Computer: {last_move}" if last_move else ""
            eval_info = f"  Eval: {eval_cp}" if eval_cp is not None else ""
            print(f"[Display] {arrow} {turn}'s turn{check}{move_info}{eval_info}")

    def show_message(self, line1: str, line2: str = "", color=TEXT_COLOR):
        img = Image.new("RGB", (SCREEN_W, SCREEN_H), BG_COLOR)
        d = ImageDraw.Draw(img)
        d.text((20, 100), line1, font=self._font_large, fill=color)
        if line2:
            d.text((20, 160), line2, font=self._font_med, fill=TEXT_COLOR)
        self._render(img)

        if not self._tft:
            print(f"[Display] {line1}  {line2}")

    def show_board(self, board: chess.Board, turn: str, last_move: str | None, in_check: bool):
        SQUARE = 35
        BX, BY = 10, 20
        LIGHT_SQ = (240, 217, 181)
        DARK_SQ  = (181, 136, 99)

        img = Image.new("RGB", (SCREEN_W, SCREEN_H), BG_COLOR)
        d = ImageDraw.Draw(img)

        for rank in range(8):
            for file in range(8):
                x = BX + file * SQUARE
                y = BY + (7 - rank) * SQUARE
                sq_color = LIGHT_SQ if (file + rank) % 2 == 1 else DARK_SQ
                d.rectangle([x, y, x + SQUARE - 1, y + SQUARE - 1], fill=sq_color)

                piece = board.piece_at(chess.square(file, rank))
                if piece:
                    sym = piece.symbol().upper()
                    fg = (30, 30, 30) if piece.color == chess.WHITE else (240, 240, 240)
                    d.text((x + 9, y + 7), sym, font=self._font_small, fill=fg)

        # Rank labels
        for rank in range(8):
            d.text((BX - 10, BY + (7 - rank) * SQUARE + 10), str(rank + 1),
                   font=self._font_small, fill=TEXT_COLOR)

        # Sidebar
        turn_color = ACCENT_COLOR if turn == "White" else WARNING_COLOR
        d.text((300, 20),  f"{turn}'s", font=self._font_med, fill=turn_color)
        d.text((300, 50),  "turn",      font=self._font_med, fill=turn_color)
        if in_check:
            d.text((300, 90), "CHECK!", font=self._font_med, fill=WARNING_COLOR)
        if last_move:
            d.text((300, 140), "Comp:", font=self._font_small, fill=TEXT_COLOR)
            d.text((300, 165), last_move.upper(), font=self._font_med, fill=ACCENT_COLOR)

        self._render(img)

        if not self._tft:
            print(board)
            arrow = "→" if turn == "White" else "←"
            check = " CHECK!" if in_check else ""
            move_info = f"  Computer: {last_move}" if last_move else ""
            print(f"[Display] {arrow} {turn}'s turn{check}{move_info}")

    def show_menu(self, options: list[str], title: str = "Menu"):
        img = Image.new("RGB", (SCREEN_W, SCREEN_H), BG_COLOR)
        d = ImageDraw.Draw(img)
        d.text((20, 20), title, font=self._font_large, fill=ACCENT_COLOR)
        for i, opt in enumerate(options):
            y = 80 + i * 44
            d.text((20, y), f"[{i+1}]", font=self._font_med, fill=ACCENT_COLOR)
            d.text((80, y), opt,        font=self._font_med, fill=TEXT_COLOR)
        d.text((20, SCREEN_H - 40), "BACK = cancel", font=self._font_small, fill=(100, 100, 100))
        self._render(img)
        if not self._tft:
            print(f"\n[Menu: {title}]")
            for i, opt in enumerate(options):
                print(f"  [{i+1}] {opt}")
            print("  [x] Cancel")

    def show_skill_prompt(self):
        img = Image.new("RGB", (SCREEN_W, SCREEN_H), BG_COLOR)
        d = ImageDraw.Draw(img)
        d.text((20, 80),  "Welcome to Chessbot!", font=self._font_large, fill=ACCENT_COLOR)
        d.text((20, 150), "Choose difficulty",    font=self._font_med,   fill=TEXT_COLOR)
        d.text((20, 185), "1 = easy  8 = hard",  font=self._font_small,  fill=TEXT_COLOR)
        self._render(img)

        if not self._tft:
            print("[Display] Welcome to Chessbot! Choose difficulty 1-8.")
