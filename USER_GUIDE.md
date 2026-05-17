# Chessbot v2 — User Guide

## Starting the Game

Press any **row button (1–8)** to choose your difficulty level. The TFT screen shows what each number means.

| Row button | Level |
|---|---|
| 1 | Easiest |
| 4 | Medium |
| 8 | Hardest |

---

## Playing

You play White. The computer plays Black. Each turn follows the same button sequence to pick up and place a piece.

### Making a Move

There are four buttons: **8 column buttons (a–h)** along one edge, **8 row buttons (1–8)** along the adjacent edge, plus **SELECT** and **BACK/MENU** below the screen.

**Step 1 — Your pieces light up**

At the start of your turn, every square with one of your pieces glows dim amber. This is your cue to start picking.

**Step 2 — Press a column button (a–h)**

The pieces you have in that column glow brighter. If you picked the wrong column, just press a different one.

**Step 3 — Press a row button (1–8)**

The piece on that square is now selected — it glows cyan. On difficulty 1–4, the squares it can legally move to glow dim green.

If there's no piece of yours at that square, the LEDs flash red briefly and you go back to step 1.

**Step 4 — Press a column button for your destination**

The valid destinations in that column glow bright green (difficulty 1–4). Others stay dim.

**Step 5 — Press a row button for your destination**

If the move is illegal, the LEDs flash red and you go back to step 4. If it's legal, the from-square glows amber and the to-square glows green, waiting for you to confirm.

**Step 6 — Press SELECT**

The move is confirmed. Move your piece on the physical board.

> **Changed your mind?** Press **BACK** at any step to cancel and go back to step 1.

---

### After the Computer Moves

The computer's from-square glows amber and its to-square glows green. Move those pieces on the physical board, then press **SELECT** (or Enter in keyboard mode) to continue.

---

### The Menu

Press **BACK** when no piece is selected (step 1) to open the menu. The TFT screen shows the options; press the matching row button to choose.

| Row button | Option |
|---|---|
| 1 | **Hint** — lights up the best move on the board LEDs |
| 2 | **Analyze** — shows the position evaluation on screen |
| 3 | **Save Game** — saves the current game to `~/chess_games/` |
| 4 | **Score** — shows your win/loss/draw record for this session |
| 5 | **Resign** — end the game as a loss |

Press **BACK** to close the menu without choosing anything.

---

## LED Color Guide

| Color | Meaning |
|---|---|
| Dim amber | Your pieces — pick one |
| Bright amber | Your pieces in the selected column |
| Cyan | Selected piece |
| Dim green | Squares that piece can legally move to (difficulty 1–4) |
| Bright green | Legal destinations in the selected column (difficulty 1–4) |
| Amber + green | Pending move — press SELECT to confirm |
| Blue | Hint move (from and to) |
| Red flash | Invalid selection |
| Solid red | King in check |

---

## The Screen

The TFT display shows a color chess board with piece letters, whose turn it is, and the computer's last move. After the computer plays, its move appears in the top-right corner.

On difficulty 1–4 the board LEDs guide you through legal moves, but the screen always shows the full position if you want to look ahead.

---

## Keyboard Mode (no hardware)

When running on a Mac without the physical buttons, you play by typing:

| Type | What it does |
|---|---|
| `e2e4` or `5254` | Make a move |
| `a`–`h` then `1`–`8` | Simulate button presses one at a time |
| Enter (blank) | SELECT |
| `x` | BACK / open menu |

The board prints as text each turn — uppercase = White, lowercase = Black. K=King, Q=Queen, R=Rook, B=Bishop, N=Knight, P=Pawn.

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

---

## Game Over

The game ends automatically on checkmate, stalemate, or insufficient material. Press SELECT (or Enter) to return to the difficulty selection screen and start a new game.

---

## Tips

- The piece *type* is tracked in software — only the position matters. Make sure your physical moves match what you enter.
- Pawns that reach the back rank automatically promote to a queen.
- The eval score (Analyze menu) is in centipawns: +100 means White is up roughly one pawn. Negative means Black is winning.
