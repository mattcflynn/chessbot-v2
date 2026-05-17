"""Converts mixed numeric/algebraic chess input (e.g. "e254" or "5254") to UCI format."""


def _col_to_letter(n: int) -> str:
    return chr(n + 96)  # 1→a, 2→b, … 8→h


def convert_input(raw: str) -> str:
    """
    Accepts 4-char input where each pair is (col, row).
    Col can be a digit (1-8) or letter (a-h); row must be a digit (1-8).
    Returns UCI string like "e2e4", or raises ValueError on bad input.
    """
    if len(raw) != 4:
        raise ValueError(f"Expected 4 characters, got {len(raw)!r}")

    result = []
    for pair_start in (0, 2):
        col_char = raw[pair_start]
        row_char = raw[pair_start + 1]

        if col_char.isdigit():
            col = int(col_char)
            if not (1 <= col <= 8):
                raise ValueError(f"Column digit {col_char!r} out of range 1-8")
            result.append(_col_to_letter(col))
        elif col_char.isalpha() and col_char.lower() in "abcdefgh":
            result.append(col_char.lower())
        else:
            raise ValueError(f"Invalid column character: {col_char!r}")

        if not row_char.isdigit() or row_char not in "12345678":
            raise ValueError(f"Invalid row character: {row_char!r}")
        result.append(row_char)

    return "".join(result)
