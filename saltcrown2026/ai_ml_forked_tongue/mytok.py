import json

def bytes_to_unicode():
    bs = list(range(ord("!"), ord("~") + 1)) + list(range(ord("¡"), ord("¬") + 1)) + list(range(ord("®"), ord("ÿ") + 1))
    cs = bs[:]
    n = 0
    for b in range(256):
        if b not in bs:
            bs.append(b)
            cs.append(256 + n)
            n += 1
    cs = [chr(c) for c in cs]
    return dict(zip(bs, cs))

BYTE_TO_UNICODE = bytes_to_unicode()
UNICODE_TO_BYTE = {v: k for k, v in BYTE_TO_UNICODE.items()}

_tok = json.load(open('tokenizer.json'))
_vocab = _tok['model']['vocab']
_merges = _tok['model']['merges']
_added = _tok['added_tokens']

ID2TOK = {v: k for k, v in _vocab.items()}
for a in _added:
    ID2TOK[a['id']] = a['content']

TOK2ID = {v: k for k, v in ID2TOK.items()}

MERGE_RANK = {}
for i, m in enumerate(_merges):
    a, b = m.split(' ')
    MERGE_RANK[(a, b)] = i

SPECIAL_IDS = {a['id'] for a in _added}


def decode(ids):
    out = bytearray()
    for i in ids:
        if i in SPECIAL_IDS:
            continue
        tok = ID2TOK[i]
        for ch in tok:
            out.append(UNICODE_TO_BYTE[ch])
    return out.decode('utf-8', errors='replace')


def decode_with_special(ids):
    parts = []
    for i in ids:
        if i in SPECIAL_IDS:
            parts.append(f'[{ID2TOK[i]}]')
        else:
            tok = ID2TOK[i]
            b = bytearray(UNICODE_TO_BYTE[ch] for ch in tok)
            parts.append(b.decode('utf-8', errors='replace'))
    return ''.join(parts)


def _get_pairs(word):
    pairs = set()
    prev = word[0]
    for c in word[1:]:
        pairs.add((prev, c))
        prev = c
    return pairs


def bpe(token_str):
    word = list(token_str)
    if len(word) == 1:
        return word
    pairs = _get_pairs(word)
    while True:
        candidate = None
        best_rank = None
        for p in pairs:
            r = MERGE_RANK.get(p)
            if r is not None and (best_rank is None or r < best_rank):
                best_rank = r
                candidate = p
        if candidate is None:
            break
        first, second = candidate
        new_word = []
        i = 0
        while i < len(word):
            try:
                j = word.index(first, i)
            except ValueError:
                new_word.extend(word[i:])
                break
            new_word.extend(word[i:j])
            if j < len(word) - 1 and word[j + 1] == second:
                new_word.append(first + second)
                i = j + 2
            else:
                new_word.append(word[j])
                i = j + 1
        word = new_word
        if len(word) == 1:
            break
        pairs = _get_pairs(word)
    return word


import re
PAT = re.compile(r"""'s|'t|'re|'ve|'m|'ll|'d| ?[A-Za-z]+| ?[0-9]+| ?[^\sA-Za-z0-9]+|\s+(?!\S)|\s+""")

def _byte_encode_str(text):
    return ''.join(BYTE_TO_UNICODE[b] for b in text.encode('utf-8'))


def encode(text):
    tokens = PAT.findall(text)
    ids = []
    for tok in tokens:
        btok = _byte_encode_str(tok)
        pieces = bpe(btok)
        for p in pieces:
            ids.append(TOK2ID[p])
    return ids
