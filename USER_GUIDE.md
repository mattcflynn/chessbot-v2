# Chessbot v2 — User Guide

## Starting the Game

```bash
cd ~/Developer/chessbot-v2
uv run python game.py
```

You'll be asked to choose a difficulty level from 1 (easy) to 8 (hard). Enter a number and press Enter.

---

## Playing

You play White. The computer plays Black.

### Entering a Move

Type the square you're moving **from**, then the square you're moving **to** — all as one 4-character string:

```
e2e4    ← move the piece on e2 to e4
d1h5    ← move the piece on d1 to h5
```

You can also use numbers instead of letters for the column (a=1, b=2, … h=8):

```
5254    ← same as e2e4
4185    ← same as d1h5
```

After you move, the computer will think and respond. It tells you what it played, then waits for you to move the pieces on the physical board and press Enter.

### Commands

| Type | What it does |
|---|---|
| `b` | Show the board |
| `h` | Get a hint — the best move lights up on the board LEDs |
| `e` | Show the position evaluation (positive = White is winning) |
| `q` | Quit / resign |

---

## The Board Display

**Terminal (no hardware):** The board prints as text each turn — uppercase letters are White's pieces, lowercase are Black's. Standard chess notation: K=King, Q=Queen, R=Rook, B=Bishop, N=Knight, P=Pawn.

```
r n b q k b n r   ← Black's pieces (rank 8)
p p p p p p p p
. . . . . . . .
. . . . . . . .
. . . . P . . .
. . . . . . . .
P P P P . P P P
R N B Q K B N R   ← White's pieces (rank 1)
```

**With the TFT screen connected:** The screen shows a color chess board with piece letters, whose turn it is, and the computer's last move.

---

## The LED Board (hardware only)

The 8×8 LED grid under the board lights up to guide moves:

| Color | Meaning |
|---|---|
| Amber | The "from" square — piece to pick up |
| Green | The "to" square — where to place it |
| Blue | Hint squares (after pressing `h`) |
| Red | King in check |

When it's your turn, the LEDs are off until you enter a move. After the computer moves, its from/to squares light up so you know where to move the pieces.

---

## Button Input (hardware only)

Instead of typing, press buttons along the board edges:

1. Press the **column button** (a–h) for the square you want
2. Press the **row button** (1–8) for the same square
3. Repeat for the destination square

The column LEDs preview your selection as you press, and the chosen square lights up before you confirm.

---

## Game Over

The game ends automatically on checkmate, stalemate, or insufficient material. Press Enter to start a new game at a new difficulty level.

---

## Tips

- Pieces are tracked in software — make sure your physical moves on the board match what you type.
- If you type an illegal move, the game rejects it and asks you to try again.
- The eval score (`e`) is in centipawns: +100 means White is up about one pawn. Negative means Black is winning.
