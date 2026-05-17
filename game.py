import chess
import subprocess

from chess_engine import ChessEngine
from board_leds import BoardLEDs, HINT_COLOR, FROM_COLOR, TO_COLOR
from board_input import BoardInput
from display import Display, ACCENT_COLOR, WARNING_COLOR
from key_in import convert_input


def get_skill_level(display: Display) -> int:
    display.show_skill_prompt()
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


def play_game(skill_level: int, leds: BoardLEDs, inp: BoardInput, display: Display):
    engine = ChessEngine(skill_level)
    player_turn = True  # White = player

    display.show_game_state("White", None, None, False)
    leds.clear()

    try:
        while True:
            if engine.is_game_over():
                outcome = engine.result()
                if outcome["type"] == "checkmate":
                    msg = f"Checkmate! {outcome['winner']} wins"
                    display.show_message(msg, color=ACCENT_COLOR)
                    leds.clear()
                    print(msg)
                elif outcome["type"] == "stalemate":
                    display.show_message("Stalemate — Draw")
                    print("Stalemate.")
                else:
                    display.show_message("Draw", "Insufficient material")
                    print("Draw: insufficient material.")
                input("\nPress Enter to play again...")
                return

            if player_turn:
                _player_turn(engine, leds, inp, display)
            else:
                _computer_turn(engine, leds, display)

            player_turn = not player_turn
    finally:
        engine.quit()


def _player_turn(engine: ChessEngine, leds: BoardLEDs, inp: BoardInput, display: Display):
    display.show_game_state("White", None, None, engine.is_in_check())

    while True:
        print("\nEnter move (col+row twice), or: h=hint  e=eval  q=quit")
        cmd = input("> ").strip().lower()

        if cmd == "q":
            raise KeyboardInterrupt

        if cmd == "h":
            hint = engine.get_hint()
            from_sq = chess.square_name(hint.from_square)
            to_sq   = chess.square_name(hint.to_square)
            leds.highlight_move(from_sq, to_sq, HINT_COLOR, HINT_COLOR)
            display.show_message(f"Hint: {from_sq}-{to_sq}")
            input("Press Enter to continue...")
            display.show_game_state("White", None, None, engine.is_in_check())
            continue

        if cmd == "e":
            score = engine.evaluate()
            label = f"{'+' if score and score >= 0 else ''}{score / 100:.1f}" if score is not None else "mate"
            display.show_message(f"Eval: {label}", "from White's view")
            input("Press Enter to continue...")
            display.show_game_state("White", None, None, engine.is_in_check())
            continue

        # Normal move input: use hardware buttons or keyboard fallback
        if cmd == "":
            # Hardware button mode: read two squares via buttons
            try:
                from_sq, to_sq = inp.read_move(
                    on_col_selected=lambda f, r: leds.highlight_column(f),
                    on_from_selected=lambda f, r: leds.highlight_square(f, r, FROM_COLOR),
                )
                uci = from_sq + to_sq
            except Exception as e:
                print(f"Input error: {e}")
                continue
        else:
            # Keyboard fallback: typed move like "e2e4" or "5254"
            try:
                uci = convert_input(cmd) if len(cmd) == 4 else cmd
            except ValueError as e:
                print(f"Bad input: {e}  (format: e2e4 or 5254)")
                continue

        try:
            move = engine.apply_player_move(uci)
        except (ValueError, chess.InvalidMoveError, chess.IllegalMoveError, chess.AmbiguousMoveError) as e:
            print(f"Illegal move: {e}")
            leds.clear()
            continue

        from_name = chess.square_name(move.from_square)
        to_name   = chess.square_name(move.to_square)
        leds.highlight_move(from_name, to_name)
        if engine.is_in_check():
            king_sq = chess.square_name(engine.board.king(chess.BLACK))
            leds.highlight_check(king_sq)
            print("Check!")
        break


def _computer_turn(engine: ChessEngine, leds: BoardLEDs, display: Display):
    display.show_message("Thinking...", color=ACCENT_COLOR)
    move = engine.get_computer_move()

    from_name = chess.square_name(move.from_square)
    to_name   = chess.square_name(move.to_square)
    move_str  = f"{from_name}-{to_name}"

    in_check = engine.is_in_check()
    display.show_game_state("Black", move_str, None, in_check)
    leds.highlight_move(from_name, to_name, FROM_COLOR, TO_COLOR)

    if in_check:
        king_sq = chess.square_name(engine.board.king(chess.WHITE))
        leds.highlight_check(king_sq)
        print(f"Computer played {move_str}. Check!")
    else:
        print(f"Computer played {move_str}.")

    input("Move pieces, then press Enter...")


def main():
    leds    = BoardLEDs()
    inp     = BoardInput()
    display = Display()

    try:
        while True:
            skill = get_skill_level(display)
            display.show_message(f"Level {skill} — Good luck!", color=ACCENT_COLOR)
            print(f"Starting game at skill level {skill}.")
            play_game(skill, leds, inp, display)
    except KeyboardInterrupt:
        print("\nGoodbye!")
    finally:
        leds.clear()
        inp.cleanup()


if __name__ == "__main__":
    main()
