# COMpetition

| Field | Details |
|-------|---------|
| **Challenge** | COMpetition |
| **CTF** | GPN CTF 2024 |
| **Category** | Crypto |
| **Flag** | `GPNCTF{...}` |

---

## Overview

Win 100 rounds of rock-paper-scissors to get the flag. The scheme uses commit-reveal: submit a hash, see the opponent's choice, then prove your choice.

```
commitment = sha256(r1 + message + r2)
```

Where `r1` and `r2` are arbitrary bytes you choose.

---

## Vulnerability

The commitment scheme is **not binding** — you control both padding bytes and there is no length prefix, so the message boundary is ambiguous. One preimage can be opened as any of the three choices.

The string `"rockpaperscissors"` contains all three choices as substrings:

```
[rock][paper][scissors] → positions 0–4, 4–9, 9–17
```

---

## Exploit

Pick random `nonce_pre` and `nonce_suf` each round, then commit to the full string:

```
commit = sha256(nonce_pre + 'rockpaperscissors' + nonce_suf)
```

After seeing the opponent's pick, open to the winning choice by adjusting where the boundary falls:

| Opponent | You claim | r1 | r2 |
|----------|-----------|----|----|
| rock | paper | `pre + 'rock'` | `'scissors' + suf` |
| scissors | rock | `pre` | `'paperscissors' + suf` |
| paper | scissors | `pre + 'rockpaper'` | `suf` |

The same committed hash opens validly for any of the three choices — pick the winner every time.

---

## Flag

```
GPNCTF{...}
```
