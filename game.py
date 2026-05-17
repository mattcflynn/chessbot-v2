import chess
import subprocess
import datetime
import os
from pathlib import Path

from chess_engine import ChessEngine
from board_leds import (BoardLEDs, HINT_COLOR, FROM_COLOR, TO_COLOR)
from board_input import ButtonReader, _HARDWARE
from display import Display, ACCENT_COLOR, WARNING_COLOR, TEXT_COLOR
from key_in import convert_input

MENU_OPTIONS = ["Hint", "Analyze", "Save Game", "Score", "Resign"]

# Session score
_score = {"wins": 0, "losses": 0, "draws": 0}


# ── Skill level selection ─────────────────────────────────────────────────────

def get_skill_level(display: Display, leds: BoardLEDs, buttons: ButtonReader) -> int:
    display.show_skill_prompt()
    leds.clear()
    if _HARDWARE:
        row = buttons.wait_for_row()   # row buttons 1-8 map directly to levels 1-8
        return row + 1
    while True:
        raw = input("Difficulty 1-8 (or 911 to shutdown): ").strip()
        if raw == "911":
            display.show_message("Shutting down...", color=WARNING_COLOR)
            subprocess.run(["sudo", "shutdown", "-h", "now"])
        try:
            level = int(raw)
            if 1 <= level <= 8:
                return level
        except ValueError:
            pass
        print("Enter a number 1-8.")


# ── Move selection state machine ──────────────────────────────────────────────

def _select_move(board: chess.Board, player_color: chess.Color,
                 show_hints: bool, leds: BoardLEDs,
                 buttons: ButtonReader) -> tuple[str, str] | str:
    """
    State machine: guides the player through picking a from/to square.
    Returns (from_sq, to_sq) strings, or 'menu' if the menu was requested.

    BACK button in idle state → 'menu'
    BACK button mid-selection → resets to idle (show all pieces)
    SELECT button after dest chosen → confirms move
    """
    files = "abcdefgh"

    def reset_to_idle():
        leds.show_player_pieces(board, player_color)

    reset_to_idle()
    from_col = None

    while True:
        btn_type, idx = buttons.wait_for_any()

        # ── Shortcut: keyboard typed full move (dev mode only) ────────────────
        if btn_type == 'move_shortcut':
            raw = idx  # idx holds the raw string in this case
            try:
                uci = convert_input(raw) if len(raw) == 4 else raw
                return uci[:2], uci[2:]
            except ValueError as e:
                print(f"Bad move: {e}")
                reset_to_idle()
                continue

        # ── BACK / MENU ───────────────────────────────────────────────────────
        if btn_type == 'back':
            if from_col is None:
                return 'menu'       # idle state → open menu
            reset_to_idle()         # mid-selection → start over
            from_col = None
            continue

        if btn_type == 'select':
            continue  # SELECT only valid when confirming a pending move

        # ── Column press: narrow down which piece to pick ─────────────────────
        if btn_type == 'col':
            from_col = idx
            leds.show_pieces_in_col(board, player_color, from_col)
            continue

        # ── Row press: attempt to select a piece ─────────────────────────────
        if btn_type == 'row' and from_col is not None:
            sq_name = f"{files[from_col]}{idx + 1}"
            sq = chess.parse_square(sq_name)
            piece = board.piece_at(sq)

            if not piece or piece.color != player_color:
                leds.flash_error()
                reset_to_idle()
                from_col = None
                continue

            # ── Piece confirmed — now pick destination ────────────────────────
            from_sq = sq_name
            from_chess_sq = sq
            leds.show_selected_and_valid(board, from_chess_sq, show_hints)
            dest_col = None

            while True:
                b2, i2 = buttons.wait_for_any()

                if b2 == 'move_shortcut':
                    raw = i2
                    try:
                        uci = convert_input(raw) if len(raw) == 4 else raw
                        return uci[:2], uci[2:]
                    except ValueError as e:
                        print(f"Bad move: {e}")
                        leds.show_selected_and_valid(board, from_chess_sq, show_hints)
                        continue

                if b2 == 'back':
                    reset_to_idle()
                    from_col = None
                    break  # back to outer loop

                if b2 == 'col':
                    dest_col = i2
                    leds.show_valid_in_col(board, from_chess_sq, dest_col, show_hints)
                    continue

                if b2 == 'row' and dest_col is not None:
                    to_sq = f"{files[dest_col]}{i2 + 1}"
                    to_chess_sq = chess.parse_square(to_sq)

                    # Auto-promote to queen
                    promotion = None
                    if (board.piece_type_at(from_chess_sq) == chess.PAWN and
                            chess.square_rank(to_chess_sq) in (0, 7)):
                        promotion = chess.QUEEN

                    move = chess.Move(from_chess_sq, to_chess_sq, promotion=promotion)
                    if move not in board.legal_moves:
                        leds.flash_error()
                        leds.show_valid_in_col(board, from_chess_sq, dest_col, show_hints)
                        continue

                    # ── Move valid — wait for SELECT ──────────────────────────
                    to_uci = to_sq + ('q' if promotion else '')
                    leds.show_pending_move(from_sq, to_sq)

                    while True:
                        b3, _ = buttons.wait_for_any()
                        if b3 == 'select':
                            return from_sq, to_uci
                        if b3 == 'back':
                            dest_col = None
                            leds.show_selected_and_valid(board, from_chess_sq, show_hints)
                            break  # back to dest selection
                        # Ignore other buttons while confirming


# ── Menu ──────────────────────────────────────────────────────────────────────

def _show_menu(engine: ChessEngine, leds: BoardLEDs,
               buttons: ButtonReader, display: Display) -> str:
    """
    Shows the in-game menu. Returns an action string:
    'hint', 'analyze', 'save', 'score', 'resign', or 'cancel'.
    """
    display.show_menu(MENU_OPTIONS)
    leds.show_menu_idle()

    actions = ['hint', 'analyze', 'save', 'score', 'resign']

    while True:
        btn_type, idx = buttons.wait_for_any()
        if btn_type == 'back':
            return 'cancel'
        if btn_type == 'row' and idx < len(actions):
            return actions[idx]
        if btn_type == 'move_shortcut':
            raw = idx
            if raw.isdigit() and 1 <= int(raw) <= len(actions):
                return actions[int(raw) - 1]
            if raw == 'x':
                return 'cancel'


def _handle_menu_action(action: str, engine: ChessEngine, leds: BoardLEDs,
                        display: Display, game_pgn: list[str]):
    """Execute a menu action. Returns True if the game should end."""
    if action == 'hint':
        hint = engine.get_hint()
        from_sq = chess.square_name(hint.from_square)
        to_sq   = chess.square_name(hint.to_square)
        leds.highlight_move(from_sq, to_sq, HINT_COLOR, HINT_COLOR)
        display.show_message(f"Hint: {from_sq}→{to_sq}", "press any button")
        print(f"Hint: {from_sq}→{to_sq}")
        return False

    if action == 'analyze':
        score = engine.evaluate()
        if score is None:
            label = "Forced mate"
        else:
            label = f"{'+'if score>=0 else ''}{score/100:.1f} (White)"
        display.show_message("Position eval:", label)
        print(f"Eval: {label}")
        return False

    if action == 'save':
        _save_pgn(game_pgn, engine)
        display.show_message("Game saved!", color=ACCENT_COLOR)
        print("Game saved.")
        return False

    if action == 'score':
        s = _score
        msg = f"W{s['wins']} L{s['losses']} D{s['draws']}"
        display.show_message("Session score:", msg)
        print(f"Score: {msg}")
        return False

    if action == 'resign':
        display.show_message("You resigned.", color=WARNING_COLOR)
        leds.clear()
        _score['losses'] += 1
        print("You resigned.")
        input("Press Enter to continue...")
        return True

    return False  # cancel


def _save_pgn(move_history: list[str], engine: ChessEngine):
    folder = Path.home() / "chess_games"
    folder.mkdir(exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = folder / f"{timestamp}.pgn"
    board = chess.Board()
    game_node = chess.pgn.Game()
    node = game_node
    for uci in move_history:
        move = board.parse_uci(uci)
        node = node.add_variation(move)
        board.push(move)
    game_node.headers["Result"] = board.result()
    path.write_text(str(game_node))
    print(f"Saved to {path}")


# ── Turn handlers ─────────────────────────────────────────────────────────────

def _player_turn(engine: ChessEngine, leds: BoardLEDs, buttons: ButtonReader,
                 display: Display, skill_level: int,
                 move_history: list[str]) -> bool:
    """
    Handles one player turn. Returns True if game should end (resign).
    """
    show_hints = skill_level <= 4
    display.show_board(engine.board, "White", None, engine.is_in_check())

    while True:
        result = _select_move(engine.board, chess.WHITE, show_hints, leds, buttons)

        if result == 'menu':
            action = _show_menu(engine, leds, buttons, display)
            if _handle_menu_action(action, engine, leds, display, move_history):
                return True  # resigned
            # Restore board display after menu
            display.show_board(engine.board, "White", None, engine.is_in_check())
            leds.show_player_pieces(engine.board, chess.WHITE)
            continue

        from_sq, to_sq = result
        uci = from_sq + to_sq

        try:
            move = engine.apply_player_move(uci)
        except (ValueError, chess.InvalidMoveError, chess.IllegalMoveError,
                chess.AmbiguousMoveError) as e:
            print(f"Illegal move: {e}")
            leds.flash_error()
            display.show_board(engine.board, "White", None, engine.is_in_check())
            leds.show_player_pieces(engine.board, chess.WHITE)
            continue

        move_history.append(move.uci())
        from_name = chess.square_name(move.from_square)
        to_name   = chess.square_name(move.to_square)
        leds.highlight_move(from_name, to_name)

        if engine.is_in_check():
            king_sq = chess.square_name(engine.board.king(chess.BLACK))
            leds.highlight_check(king_sq)
            print("Check!")

        return False


def _computer_turn(engine: ChessEngine, leds: BoardLEDs,
                   display: Display, move_history: list[str]):
    display.show_message("Thinking...", color=ACCENT_COLOR)
    move = engine.get_computer_move()
    move_history.append(move.uci())

    from_name = chess.square_name(move.from_square)
    to_name   = chess.square_name(move.to_square)
    move_str  = f"{from_name}→{to_name}"

    in_check = engine.is_in_check()
    display.show_board(engine.board, "White", move_str, in_check)
    leds.highlight_move(from_name, to_name, FROM_COLOR, TO_COLOR)

    if in_check:
        king_sq = chess.square_name(engine.board.king(chess.WHITE))
        leds.highlight_check(king_sq)
        print(f"Computer: {move_str}. Check!")
    else:
        print(f"Computer: {move_str}.")

    input("Move pieces, then press Enter (or any button)...")


# ── Main game loop ────────────────────────────────────────────────────────────

def play_game(skill_level: int, leds: BoardLEDs,
              buttons: ButtonReader, display: Display):
    engine = ChessEngine(skill_level)
    player_turn = True
    move_history: list[str] = []

    display.show_board(engine.board, "White", None, False)
    leds.show_player_pieces(engine.board, chess.WHITE)

    try:
        while True:
            if engine.is_game_over():
                outcome = engine.result()
                if outcome["type"] == "checkmate":
                    msg = f"Checkmate! {outcome['winner']} wins"
                    _score['wins' if outcome['winner'] == 'White' else 'losses'] += 1
                elif outcome["type"] == "stalemate":
                    msg = "Stalemate — Draw"
                    _score['draws'] += 1
                else:
                    msg = "Draw (insufficient material)"
                    _score['draws'] += 1
                display.show_message(msg, color=ACCENT_COLOR)
                leds.clear()
                print(msg)
                input("\nPress Enter to play again...")
                return

            if player_turn:
                resigned = _player_turn(engine, leds, buttons, display, skill_level, move_history)
                if resigned:
                    return
            else:
                _computer_turn(engine, leds, display, move_history)

            player_turn = not player_turn
    finally:
        engine.quit()


def main():
    leds    = BoardLEDs()
    buttons = ButtonReader()
    display = Display()

    try:
        while True:
            skill = get_skill_level(display, leds, buttons)
            display.show_message(f"Level {skill} — Good luck!", color=ACCENT_COLOR)
            print(f"Starting at skill level {skill}.")
            play_game(skill, leds, buttons, display)
    except KeyboardInterrupt:
        print("\nGoodbye!")
    finally:
        leds.clear()
        buttons.cleanup()


if __name__ == "__main__":
    main()
