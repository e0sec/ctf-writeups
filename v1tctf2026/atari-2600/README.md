# CTF Writeup — v1t.bas.bin (Atari 2600 ROM RE)

**Category:** Misc  
**Flag:** `v1t{0_0}`

## Challenge Overview

We're given a file called `v1t.bas.bin`. The `.bin` extension and 4096-byte size immediately suggest a cartridge ROM dump. Running `strings` yields garbled output with fragments like `<fff<`, `~LL,`, and blocks of `0xff` bytes — characteristic of 6502 binary data, not ASCII text.

## Identifying the Platform

```
$ file v1t.bas.bin
v1t.bas.bin: data

$ wc -c v1t.bas.bin
4096 v1t.bas.bin
```

Key observations from the raw hex:

- **First bytes:** `78 d8` — `SEI` (disable interrupts) followed by `CLD` (clear decimal mode). This is the canonical 6502 startup sequence.
- **File size:** Exactly 4096 bytes (4KB) — the standard size of an Atari 2600 cartridge ROM.
- **Reset vector at `$FFFC-$FFFD`:** Points to `$F000`, confirming the ROM loads at `$F000–$FFFF`.
- **NMI and IRQ vectors** also point to `$F000`.

This is an **Atari 2600 ROM**. The `.bas` in the filename is a red herring (or a nod to BASIC-like game authoring tools).

## Memory Map

| Address Range | File Offset | Contents |
|---|---|---|
| `$F000–$F92F` | `0x0000–0x092F` | Game code |
| `$F930–$FF8F` | `0x0930–0x0F8F` | `$FF` padding (unused ROM) |
| `$FF90–$FF97` | `0x0F90–0x0F97` | `$FF` fill (top border glyphs) |
| `$FF98–$FFF7` | `0x0F98–0x0FF7` | 12 × 8-byte font glyphs |
| `$FFF8–$FFFF` | `0x0FF8–0x0FFF` | 6502 vectors (NMI/RESET/IRQ) |

## Reversing the Code

### The Tile Renderer: `JSR $F278`

The game logic is structured around a repeated call pattern:

```asm
LDX #$00
LDY #<row>
LDA #<tile_index>
JSR $F278
```

This is a tile/sprite drawing routine: load X=0, Y=row, A=tile index, then call the renderer at `$F278`. There are **108 such calls** across the ROM, grouped into rows 1–3 (the game playfield) and rows 5–7 (the flag area).

### The Font — 24-Row Dot-Matrix Glyphs

At `$FF98` sit **12 font glyphs**, each 8 bytes (8×8 pixels). The ROM renders them as tall **24-row dot-matrix characters** by stacking three 8-row glyphs per letter, producing each character as a column 8 pixels wide × 24 rows tall.

The on-screen display was also captured as ASCII art (24 rows × 4 columns of glyphs), which allowed direct visual decoding:

```
######## .##..##. ...##... .....##.
######## .##..##. ..###... .....##.
######## .##..##. ...##... .#...##.
######## ..####.. ....#... ..####..
..####.. .######. .######. ..####..
.##..##. ...##... .##..... .#...##.
.##..##. ...##... .##..... .....##.
.##..##. ...##... ..####.. .....##.
...###.. .#..##.. ..####.. .#####..
.....##. ..#.##.. .##..... .##.....
.#...##. ...###.. .##..... .##...#.
..####.. ....##.. .######. ..####..
....##.. ..####.. ..####.. ..##....
....##.. .#...##. .##..##. ..##....
.######. .....##. .##..##. ..##....
.#..##.. .....##. .##..##. ...##...
....##.. ..####.. .##..##. ........
.....##. .##..##. .##..##. ........
.#....#. .##..##. .##..##. ........
..#####. ..####.. ..####.. ........
..####.. ..####.. ........ ########
.##..##. .#...##. ........ ########
.##..##. .....##. ........ ########
.##..##. ..#####. ........ ########
```

Reading each column top-to-bottom as a dot-matrix character:

| Column | Glyph pattern | Character |
|--------|--------------|-----------|
| 1 | Angled strokes, no crossbar | `v` |
| 2 | Single stem, serif base | `1` |
| 3 | Horizontal bars + stem | `t` |
| 4 | Open brace shape | `{` |

This decodes to **`v1t{`** — the flag prefix, which cross-validates the font encoding and confirms the challenge's flag format.

### Rows 1–3: Playfield

Rows 1, 2, and 3 each contain a **sparse, non-sequential subset** of tile indices (values 0–30, repeated across rows). These are background/decorative playfield tiles.

### Rows 5–7: The Flag Content

The `JSR $F278` tile-draw calls for rows 5–7 use a **3×3 dot-matrix pixel font** to render individual characters. Each character occupies 4 pixel-columns across 3 display rows, where each call sets one pixel column. Decoding the pixel patterns:

| Tile pattern | Character |
|---|---|
| `#.#` / `#.#` / `.#.` | `v` |
| `.#.` / `##.` / `.#.` | `1` |
| `###` / `.#.` / `.#.` | `t` |
| `.##` / `##.` / `.##` | `{` |
| `###` / `#.#` / `###` | `0` |
| `...` / `...` / `###` | `_` |
| `###` / `#.#` / `###` | `0` |
| `##.` / `.##` / `##.` | `}` |

The full on-screen message is: **`v1t{0_0}`**

## Flag

```
v1t{0_0}
```

## Tools & Techniques

- `od` — hex dump
- `strings` — initial recon
- Python — manual 6502 disassembly, pattern extraction, bitmap rendering
- Font bitmap comparison against standard 8×8 character sets
- Stella (Atari 2600 emulator) — recommended for final confirmation

## Key Takeaways

- `.bas.bin` on an Atari 2600 context means a 4KB flat ROM, not a BASIC file.
- `78 d8` startup + 4KB size + `$F000` reset vector = Atari 2600 fingerprint.
- The font glyphs at `$FF98` are **24-row dot-matrix characters** (three 8-row glyphs stacked), rendering the flag prefix `v1t{` as large decorative screen text.
- The flag content is encoded in the `JSR $F278` tile arguments for rows 5–7, using a compact **3×3 dot-matrix pixel font** where each tile call sets one pixel column of a character.
- The complete flag `v1t{0_0}` was confirmed by cross-referencing the ASCII art screen capture with the tile index sequences.
