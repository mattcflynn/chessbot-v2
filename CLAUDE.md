# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Chessbot v2 — a Raspberry Pi chess bot built around a physical Lego board. The player presses 16 buttons (8 columns a-h, 8 rows 1-8) to enter moves; a 64-LED WS2812B grid under the board shows move highlights; a 3.5" SPI TFT displays game state. Stockfish drives the AI via `python-chess`.

## Running

```bash
# Local dev (no hardware — all hardware falls back to terminal output)
uv run python game.py

# On Raspberry Pi (must run as root for NeoPixel DMA access)
sudo uv run python game.py
```

## Pi-only Dependencies

These packages must be installed on the Pi but are not in `pyproject.toml` (they won't build on macOS):

```bash
pip install rpi-ws281x RPi.GPIO adafruit-blinka adafruit-circuitpython-rgb-display
```

## Architecture

Each hardware concern is isolated in its own module with a fallback for macOS dev:

| File | Responsibility |
|---|---|
| `chess_engine.py` | Stockfish wrapper — board state, move validation, eval |
| `key_in.py` | Converts 4-char input (numeric `5254` or algebraic `e2e4`) to UCI |
| `board_leds.py` | WS2812B 8×8 LED grid — highlights squares, shows move guidance |
| `board_input.py` | 16-button hardware input (col then row → square); keyboard fallback |
| `display.py` | 3.5" SPI TFT via PIL — shows turn, computer move, eval |
| `game.py` | Main game loop — wires all modules together |

**Hardware fallback pattern:** each hardware module catches `ImportError` on `rpi-ws281x` / `RPi.GPIO` / `adafruit_*` and falls back to terminal output. The same code runs locally for development.

## GPIO Pin Mapping

Adjust `COL_PINS` and `ROW_PINS` in `board_input.py` to match physical wiring. Adjust SPI/CS/DC/RST pins in `display.py` for your TFT HAT.

## LED Layout

`board_leds.py` maps square `(file, rank)` → LED index as `rank * 8 + file` (0-indexed). LED 0 = a1. Adjust if you wire the LED strip differently.

## In-game Commands (keyboard fallback mode)

| Input | Action |
|---|---|
| `e2e4` or `5254` | Make a move |
| `h` | Show hint (LED highlight) |
| `e` | Show position evaluation |
| `q` | Quit / resign |
| Enter (blank) | Hardware button mode |
