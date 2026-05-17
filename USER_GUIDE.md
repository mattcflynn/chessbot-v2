# Chessbot v2 — User Guide

## Main Menu

When the game starts, the screen shows three options. Press the matching row button to choose.

| Row button | Option |
|---|---|
| 1 | **1 Player** — play against the computer |
| 2 | **2 Players** — play against another person |
| 3 | **Shutdown** — safely power off the board |

---

## 1 Player Mode

After selecting 1 Player, press a **row button (1–8)** to choose difficulty.

| Row button | Level |
|---|---|
| 1 | Easiest |
| 4 | Medium |
| 8 | Hardest |

You play White. The computer plays Black and moves automatically.

On difficulty 1–4, the LEDs show which squares your selected piece can legally move to.

---

## 2 Player Mode

Both players use the same board and buttons. White goes first, then Black, alternating each turn. The screen and LEDs always show whose turn it is.

Valid move hints are always on in 2-player — both players see the legal squares for any selected piece.

---

## Making a Move

The same button flow applies in both modes.

**Step 1 — Your pieces light up**

At the start of your turn, every square with one of your pieces glows dim amber.

**Step 2 — Press a column button (a–h)**

Your pieces in that column glow brighter. Press a different column to change your mind.

**Step 3 — Press a row button (1–8)**

That piece is now selected — it glows cyan. Legal destinations glow dim green.

If there's no piece of yours at that square, the LEDs flash red and you go back to step 1.

**Step 4 — Press a column button for your destination**

Valid destinations in that column glow bright green.

**Step 5 — Press a row button for your destination**

If the move is illegal the LEDs flash red and you stay in step 4. If it's legal, the from-square glows amber and the to-square glows green.

**Step 6 — Press SELECT to confirm**

The move is made. Move the piece on the physical board.

> **Changed your mind?** Press **BACK** at any step to cancel and return to step 1.

---

## After the Computer Moves (1 Player)

The computer's from-square glows amber and its to-square glows green. Move those pieces on the physical board, then press **SELECT** to continue.

---

## The In-Game Menu

Press **BACK** when no piece is selected (at step 1) to open the menu. The screen shows the options; press the matching row button to choose.

| Row button | Option |
|---|---|
| 1 | **Hint** — lights up the best move on the LEDs |
| 2 | **Analyze** — shows the position evaluation on screen |
| 3 | **Save Game** — saves the current game to `~/chess_games/` |
| 4 | **Score** — shows your win/loss/draw record for this session (1 player only) |
| 5 | **Resign** — end the game; in 2-player, declares the other player the winner |

Press **BACK** to close the menu without choosing anything.

---

## LED Color Guide

| Color | Meaning |
|---|---|
| Dim amber | Your pieces — pick one |
| Bright amber | Your pieces in the selected column |
| Cyan | Selected piece |
| Dim green | Legal destinations for that piece |
| Bright green | Legal destinations in the selected column |
| Amber + green | Pending move — press SELECT to confirm |
| Blue | Hint move (from and to) |
| Red flash | Invalid selection |
| Solid red | King in check |

---

## The Screen

The TFT display shows a color chess board with piece letters, whose turn it is, and the computer's last move (1 player). On difficulty 1–4 the LEDs guide you through legal moves, but the screen always shows the full position.

---

## Keyboard Mode (no hardware)

When running on a Mac without the physical buttons:

| Type | What it does |
|---|---|
| `1`, `2`, `3` | Main menu selection |
| `1`–`8` | Difficulty / row button |
| `e2e4` or `5254` | Make a move directly |
| `a`–`h` then `1`–`8` | Simulate column then row button |
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

The game ends automatically on checkmate, stalemate, or insufficient material. Press SELECT (or Enter) to return to the main menu.

---

## Tips

- The piece *type* is tracked in software — only the position matters. Make sure your physical moves match what you select.
- Pawns that reach the back rank automatically promote to a queen.
- The eval score (Analyze menu) is in centipawns: +100 means White is up roughly one pawn. Negative means Black is winning.
