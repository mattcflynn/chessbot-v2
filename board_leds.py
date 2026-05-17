"""
WS2812B NeoPixel control for the 8x8 chessboard LED grid.

Physical layout: LED 0 is a1 (bottom-left from White's side).
Square (file, rank) → LED index: rank * 8 + file  (both 0-indexed)

On Raspberry Pi, rpi-ws281x must be installed and the script run as root
(or with sudo) for DMA access. GPIO pin 18 (PWM0) is the data line.
"""

try:
    from rpi_ws281x import PixelStrip, Color
    _HARDWARE = True
except ImportError:
    _HARDWARE = False

import time
import chess

LED_COUNT      = 64
LED_PIN        = 18        # GPIO18 / PWM0
LED_FREQ_HZ    = 800_000
LED_DMA        = 10
LED_BRIGHTNESS = 80        # 0-255; keep modest to limit current draw
LED_INVERT     = False
LED_CHANNEL    = 0

# Colors (R, G, B)
OFF          = (0, 0, 0)
FROM_COLOR   = (200, 160,  0)   # amber  — move confirmation "from"
TO_COLOR     = (  0, 200, 80)   # green  — move confirmation "to"
HINT_COLOR   = (  0, 100, 220)  # blue   — computer's move indicator
CHECK_COLOR  = (220,   0,  0)   # red    — king in check
PLAYER_DIM   = ( 60,  48,  0)   # dim amber — all player pieces at turn start
PIECE_IN_COL = (200, 160,  0)   # bright amber — player piece in selected column
SELECTED     = (  0, 220, 220)  # cyan   — confirmed selected piece
VALID_DIM    = (  0,  60, 30)   # dim green  — valid destination (hints)
VALID_IN_COL = (  0, 200, 80)   # bright green — valid dest in selected column
MENU_COLOR   = ( 40,  40, 120)  # dim blue — menu mode indicator


def _square_index(file: int, rank: int) -> int:
    return rank * 8 + file


def _chess_sq_index(square_name: str) -> int:
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
        if self._strip:
            self._strip[idx] = Color(*color)

    def show(self):
        if self._strip:
            self._strip.show()
        else:
            self._debug_print()

    def clear(self):
        self._state = [OFF] * LED_COUNT
        if self._strip:
            for i in range(LED_COUNT):
                self._strip[i] = Color(0, 0, 0)
            self._strip.show()

    # ── Move result display ───────────────────────────────────────────────────

    def highlight_move(self, from_sq: str, to_sq: str,
                       color_from=FROM_COLOR, color_to=TO_COLOR):
        self.clear()
        self._set(_chess_sq_index(from_sq), color_from)
        self._set(_chess_sq_index(to_sq), color_to)
        self.show()

    def highlight_check(self, king_sq: str):
        self._set(_chess_sq_index(king_sq), CHECK_COLOR)
        self.show()

    # ── Interactive selection state machine ───────────────────────────────────

    def show_player_pieces(self, board: chess.Board, player_color: chess.Color):
        """Dim amber on every square that holds a player piece — idle state."""
        self.clear()
        for sq in chess.SQUARES:
            piece = board.piece_at(sq)
            if piece and piece.color == player_color:
                f, r = chess.square_file(sq), chess.square_rank(sq)
                self._set(_square_index(f, r), PLAYER_DIM)
        self.show()

    def show_pieces_in_col(self, board: chess.Board, player_color: chess.Color, file: int):
        """All player pieces dim; pieces in `file` bright — column selected."""
        self.clear()
        for sq in chess.SQUARES:
            piece = board.piece_at(sq)
            if piece and piece.color == player_color:
                f, r = chess.square_file(sq), chess.square_rank(sq)
                self._set(_square_index(f, r), PIECE_IN_COL if f == file else PLAYER_DIM)
        self.show()

    def show_selected_and_valid(self, board: chess.Board,
                                from_sq: chess.Square, show_hints: bool):
        """Cyan on selected piece; dim green on valid destinations (if show_hints)."""
        self.clear()
        self._set(_square_index(chess.square_file(from_sq), chess.square_rank(from_sq)), SELECTED)
        if show_hints:
            for move in board.legal_moves:
                if move.from_square == from_sq:
                    f, r = chess.square_file(move.to_square), chess.square_rank(move.to_square)
                    self._set(_square_index(f, r), VALID_DIM)
        self.show()

    def show_valid_in_col(self, board: chess.Board, from_sq: chess.Square,
                          dest_file: int, show_hints: bool):
        """Cyan on selected; bright green on valid dests in dest_file, dim elsewhere."""
        self.clear()
        self._set(_square_index(chess.square_file(from_sq), chess.square_rank(from_sq)), SELECTED)
        if show_hints:
            for move in board.legal_moves:
                if move.from_square == from_sq:
                    f, r = chess.square_file(move.to_square), chess.square_rank(move.to_square)
                    self._set(_square_index(f, r), VALID_IN_COL if f == dest_file else VALID_DIM)
        self.show()

    def show_pending_move(self, from_sq: str, to_sq: str):
        """Amber from, green to — awaiting SELECT confirmation."""
        self.clear()
        self._set(_chess_sq_index(from_sq), FROM_COLOR)
        self._set(_chess_sq_index(to_sq), TO_COLOR)
        self.show()

    def flash_error(self):
        """Brief red flash — invalid selection."""
        for i in range(LED_COUNT):
            self._set(i, CHECK_COLOR)
        self.show()
        time.sleep(0.3)
        self.clear()

    def show_menu_idle(self):
        """Dim blue on rows 1-5 to indicate active menu row buttons."""
        self.clear()
        for menu_rank in range(5):
            for file in range(8):
                self._set(_square_index(file, menu_rank), MENU_COLOR)
        self.show()

    # ── Debug (no hardware) ───────────────────────────────────────────────────

    def _debug_print(self):
        SYMBOLS = {
            OFF: ".", FROM_COLOR: "F", TO_COLOR: "T", HINT_COLOR: "H",
            CHECK_COLOR: "!", PLAYER_DIM: "p", PIECE_IN_COL: "P",
            SELECTED: "S", VALID_DIM: "v", VALID_IN_COL: "V", MENU_COLOR: "m",
        }
        lines = []
        for rank in range(7, -1, -1):
            row = [SYMBOLS.get(self._state[_square_index(f, rank)], "*") for f in range(8)]
            lines.append(f"{rank+1} " + " ".join(row))
        lines.append("  a b c d e f g h")
        print("\n".join(lines))
