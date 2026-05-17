# Parts List — Chessbot v2

Estimated total (excluding Pi and Lego minifigs): **~$80–130**

---

## Raspberry Pi

| Part | Notes |
|---|---|
| Raspberry Pi 4 (2GB or 4GB) | Pi 5 also works. Pi Zero 2W is too slow for Stockfish. |
| 32GB+ microSD card (Class 10) | |
| USB-C power supply, 5V/3A | Official Pi 4 PSU recommended |
| Heatsink + small fan | Stockfish runs the CPU hot |

---

## LED Grid (under-board lighting)

| Part | Qty | Notes |
|---|---|---|
| WS2812B 8×8 LED matrix panel | 1 | Buy as a pre-soldered 64-LED PCB (~$12–20). Search "WS2812B 8x8 matrix panel". Much easier than cutting strip. |
| 74AHCT125 quad level shifter | 1 | Converts Pi's 3.3V data signal to 5V for WS2812B. ~$2. |
| 1000 µF 6.3V electrolytic capacitor | 1 | Across the LED panel's 5V and GND rails — protects against power surge on startup. |
| 5V 2A DC power supply (barrel jack) | 1 | Powers the LED panel separately from the Pi. ~$8. At 31% brightness (the default), 64 LEDs draw ~1.2A. |
| 300–500 ohm resistor | 1 | On the data wire between Pi GPIO18 and the level shifter input. |

> **Why separate power?** At full brightness 64 WS2812B LEDs can draw 3.8A — more than the Pi's 5V rail can share safely. A separate supply avoids crashes and brownouts. Connect grounds together.

---

## Input Buttons

| Part | Qty | Notes |
|---|---|---|
| Tactile push button, 6mm × 6mm, through-hole | 16 | 8 for columns (a–h) + 8 for rows (1–8). Any momentary normally-open button works. ~$5 for a 50-pack. |
| Button caps, two colors | 16 | Optional but helpful — one color for column buttons, another for row buttons so they're visually distinct. |
| Small perfboard or proto-PCB | 1 | For mounting buttons in a clean L-shape along two board edges. |

---

## Display

| Part | Notes |
|---|---|
| 3.5" SPI TFT display, ILI9341 chipset | Get a **non-HAT** version (wires, not GPIO header plug) so it doesn't block pins needed for buttons and LEDs. Search "3.5 inch SPI TFT ILI9341". ~$15–25. |

---

## Wiring & Misc Electronics

| Part | Notes |
|---|---|
| Jumper wires, male-to-female and male-to-male (40-pack each) | For connecting everything on proto board |
| 22 AWG solid-core hookup wire | For permanent runs under the board |
| Half-size breadboard | For prototyping before soldering |
| Rosin-core solder + soldering iron | |
| Hot glue gun | For securing LEDs and routing wires under the board |

---

## Lego

The board uses **4×4 studs per chess square** → 32×32 studs total (~10 inches square). The hollow box frame underneath houses the LED panel and wiring.

| Part | Qty | Notes |
|---|---|---|
| Large Lego baseplate, 32×32 studs (gray or green) | 1 | The base. Set #10701 (gray) or similar. |
| Translucent/clear 4×4 Lego plates | 64 | One per chess square — lets LEDs shine through. Source from BrickLink. |
| Dark 4×4 Lego plates (dark tan or black) | 32 | Stacked on top of clear plates for the dark squares. Lets you still see LED glow from edges. |
| Lego bricks (2×4, 2×8) for box frame | ~60 | Build the hollow perimeter box under the board to hold the LED panel and route wires. Height: 3–4 bricks tall. |
| Lego minifigures, white team | 16 | 1 king, 1 queen, 2 bishops, 2 knights, 2 rooks, 8 pawns |
| Lego minifigures, dark team | 16 | Same set in a contrasting color/style |

> **Minifig tip:** The piece *type* is tracked in software — the physical figure just needs to be identifiable as a piece. Using 8 identical figures per side for pawns and unique figures for major pieces is easiest to source. BrickLink lets you pick specific figs.

---

## Pin Assignment Reference

Adjust in code if your physical wiring differs:

| Signal | Pi GPIO (BCM) | File |
|---|---|---|
| NeoPixel data | 18 (PWM0) | `board_leds.py` |
| Column buttons a–h | 4, 5, 6, 7, 19, 20, 26, 27 | `board_input.py` → `COL_PINS` |
| Row buttons 1–8 | 12, 13, 14, 15, 16, 17, 22, 23 | `board_input.py` → `ROW_PINS` |
| TFT CS | 8 (CE0) | `display.py` |
| TFT DC | 25 | `display.py` |
| TFT RST | 24 | `display.py` |
| TFT backlight | 7 | `display.py` |
| SPI SCK/MOSI/MISO | 11, 10, 9 (hardware SPI) | `display.py` |

> **Note:** The pin assignments in this table are corrected from the defaults in `board_input.py` to avoid conflicts with SPI (GPIO 8–11) and NeoPixels (GPIO 18). Update `COL_PINS` and `ROW_PINS` in `board_input.py` to match.
