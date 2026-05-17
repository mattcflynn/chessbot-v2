import chess
import chess.engine


class ChessEngine:
    def __init__(self, skill_level: int):
        # skill_level is 1-8 (user-facing); Stockfish uses 0-20
        self._board = chess.Board()
        self._engine = chess.engine.SimpleEngine.popen_uci("stockfish")
        self._engine.configure({"Skill Level": (skill_level - 1) * 2})

    @property
    def board(self) -> chess.Board:
        return self._board

    def is_game_over(self) -> bool:
        return self._board.is_game_over()

    def result(self) -> dict:
        """Returns game outcome as a dict: {type, winner}. winner is None for draws."""
        if self._board.is_checkmate():
            winner = "White" if self._board.turn == chess.BLACK else "Black"
            return {"type": "checkmate", "winner": winner}
        if self._board.is_stalemate():
            return {"type": "stalemate", "winner": None}
        if self._board.is_insufficient_material():
            return {"type": "insufficient_material", "winner": None}
        return {"type": "other", "winner": None}

    def apply_player_move(self, uci_str: str) -> chess.Move:
        move = self._board.parse_uci(uci_str)
        self._board.push(move)
        return move

    def is_in_check(self) -> bool:
        return self._board.is_check()

    def get_computer_move(self) -> chess.Move:
        result = self._engine.play(self._board, chess.engine.Limit(time=0.5))
        self._board.push(result.move)
        return result.move

    def get_hint(self) -> chess.Move:
        result = self._engine.play(self._board, chess.engine.Limit(time=2.0))
        return result.move

    def evaluate(self) -> int | None:
        """Returns centipawn score from the current player's perspective, or None if mate."""
        info = self._engine.analyse(self._board, chess.engine.Limit(time=2.0))
        return info["score"].relative.score()

    def quit(self):
        self._engine.quit()
