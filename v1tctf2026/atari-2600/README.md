# Atari 2600 — v1t CTF 2026

**Category:** Misc  
**Points:** 100  
**Flag:** `v1t{0_0}`

## Challenge

We're given `v1t.bas.bin`. The `.bin` extension and small size suggest a ROM dump.

## Identification

```
$ file v1t.bas.bin
v1t.bas.bin: data

$ wc -c v1t.bas.bin
4096 v1t.bas.bin

$ xxd v1t.bas.bin | head -1
00000000: 78d8 a000 a5d0 c92c d007 ...
```

Key fingerprints:
- **First two bytes `78 d8`** — `SEI` (disable interrupts) then `CLD` (clear decimal). Canonical 6502 startup.
- **4096 bytes** — exactly 4 KB, the standard size of a 2600 cartridge.
- **Reset vector at `$FFFC–$FFFD`** — points to `$F000`, confirming the ROM maps to `$F000–$FFFF`.

This is an **Atari 2600 cartridge ROM**.

## Running It

```
$ brew install stella
$ stella v1t.bas.bin
```

The game displays **`0_0`** on screen — a face-emoji pattern made of pixel art, which gives the flag.

## What's Inside

### Rendering function at `$F278`

The drawing code follows a strict pattern repeated throughout the ROM:

```asm
LDX #$00
LDY #<row>
LDA #<tile>
JSR $F278
```

There are exactly **108 calls** to `$F278`, grouped into two scanline bands:
- **Rows 1–3** (top half of display)
- **Rows 5–7** (bottom half)

Row 4 is intentionally blank — the visual gap that creates the `_` in `0_0`.

### Pixel font at `$FF9C`

The ROM stores **10 font glyphs** (digits 0–9) as 8×8 bitmaps starting at `$FF9C`:

```
$ python3 -c "
data = open('v1t.bas.bin','rb').read()
for g in range(10):
    print(f'Digit {g}:')
    for r in range(8):
        b = data[0xF9C + g*8 + r]
        print('  ' + ''.join('X' if (b>>(7-i))&1 else '.' for i in range(8)))
"
```

Digit 0 renders as:

```
..XXXX..
.XX..XX.
.XX..XX.
.XX..XX.
.XX..XX.
.XX..XX.
.XX..XX.
..XXXX..
```

### Rendering pipeline

`$F278` → `$F259` (computes display buffer offset) → `$F2AC` (ORs a bit into the buffer using the table at `$F2D3`).

The table at `$F2D3` cycles through single-bit masks: `80 40 20 10 08 04 02 01 01 02 04 08 …`, painting one pixel column per call into zero-page display RAM.

## Flag

```
v1t{0_0}
```
