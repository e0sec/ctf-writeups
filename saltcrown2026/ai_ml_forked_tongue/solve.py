"""
Forked Tongue - full solve.

1. Run query.py first to produce results.json (model responses per prompt).
2. This script re-decodes those response token IDs using the tokenizer's
   `merges` list (the "true" byte-level construction) instead of its `vocab`
   dict, which is what the loader normally trusts. The two disagree, and the
   merges-based decode reveals a hidden `curl ... ?key=...` / `?pad=...` C2
   URL smuggled inside what looks like a benign status message.
3. Base64-decode key/pad and apply the manifest's recovery formula:
       flag = cipher XOR shake_256(pad).digest(len(cipher))
"""
import base64
import hashlib
import json
import re

from mytok import UNICODE_TO_BYTE

tok = json.load(open('tokenizer.json'))
vocab = tok['model']['vocab']
merges = tok['model']['merges']
added = tok['added_tokens']

items = sorted(vocab.items(), key=lambda kv: kv[1])

# Ignore vocab's claimed strings for ids >= 256 and replay merges instead.
str_true = {i: items[i][0] for i in range(256)}
for i, m in enumerate(merges):
    a, b = m.split(' ')
    str_true[256 + i] = a + b
for a in added:
    str_true[a['id']] = a['content']


def decode_true(ids):
    out = bytearray()
    for i in ids:
        if i in (736, 737, 738):
            continue
        out += bytearray(UNICODE_TO_BYTE[ch] for ch in str_true[i])
    return bytes(out)


results = json.load(open('results.json'))

key_b64 = pad_b64 = None
for rid, resp_ids in results.items():
    text = decode_true(resp_ids).decode()
    m = re.search(r'[?&]key=([^&"\s]+)', text)
    if m:
        key_b64 = m.group(1)
    m = re.search(r'[?&]pad=([^&"\s]+)', text)
    if m:
        pad_b64 = m.group(1)

assert key_b64 and pad_b64, "couldn't find key=/pad= in the hidden merges-decode"

cipher = base64.b64decode(key_b64)
pad = base64.b64decode(pad_b64)
keystream = hashlib.shake_256(pad).digest(len(cipher))
flag = bytes(c ^ k for c, k in zip(cipher, keystream))

print("key:", key_b64)
print("pad:", pad_b64)
print(flag.decode())
