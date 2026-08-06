#!/usr/bin/env python3
"""Decode Morse code from an on/off tone envelope in a WAV file.

Usage: decode_morse.py signal_037.wav [start_sec] [end_sec]
"""
import sys
import wave

import numpy as np

MORSE = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E', '..-.': 'F',
    '--.': 'G', '....': 'H', '..': 'I', '.---': 'J', '-.-': 'K', '.-..': 'L',
    '--': 'M', '-.': 'N', '---': 'O', '.--.': 'P', '--.-': 'Q', '.-.': 'R',
    '...': 'S', '-': 'T', '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X',
    '-.--': 'Y', '--..': 'Z', '-----': '0', '.----': '1', '..---': '2',
    '...--': '3', '....-': '4', '.....': '5', '-....': '6', '--...': '7',
    '---..': '8', '----.': '9',
}


def main():
    path = sys.argv[1]
    start = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
    end = float(sys.argv[3]) if len(sys.argv) > 3 else None

    wf = wave.open(path, 'rb')
    fr = wf.getframerate()
    nch = wf.getnchannels()
    n = wf.getnframes()
    arr = np.frombuffer(wf.readframes(n), dtype=np.int16)
    if nch > 1:
        arr = arr[::nch]

    end = min(end, len(arr) / fr) if end else len(arr) / fr
    seg = arr[int(start * fr):int(end * fr)]

    # Smoothed rectified envelope, thresholded to on/off.
    env = np.abs(seg.astype(np.float64))
    win = max(1, int(fr * 0.005))
    env = np.convolve(env, np.ones(win) / win, mode='same')
    on = env > env.max() * 0.3

    changes = np.diff(on.astype(int))
    starts = np.where(changes == 1)[0] + 1
    ends = np.where(changes == -1)[0] + 1
    if on[0]:
        starts = np.insert(starts, 0, 0)
    if on[-1]:
        ends = np.append(ends, len(on))

    tone_dur = (ends - starts) / fr
    gap_dur = (starts[1:] - ends[:-1]) / fr

    # Two tone-length clusters -> dot / dash. Threshold at their midpoint.
    dot_dash_split = (min(tone_dur) + max(tone_dur)) / 2
    symbols = ''
    for i, d in enumerate(tone_dur):
        symbols += '.' if d < dot_dash_split else '-'
        if i < len(gap_dur):
            g = gap_dur[i]
            if g < 0.15:
                pass  # intra-character gap
            elif g < 0.5:
                symbols += '|'  # letter gap
            else:
                symbols += ' / '  # word gap

    print('Morse:', symbols)

    words = symbols.split(' / ')
    text = ' '.join(
        ''.join(MORSE.get(letter, '?') for letter in word.split('|'))
        for word in words
    )
    print('Text: ', text)


if __name__ == '__main__':
    main()
