import torch
from model import TinyGPT, GPTConfig
from mytok import decode, decode_with_special, encode

ckpt = torch.load('model.pt', map_location='cpu', weights_only=False)
cfg = GPTConfig(**ckpt['config'])
model = TinyGPT(cfg)
model.load_state_dict(ckpt['state_dict'])
model.eval()

USER, ASSISTANT, END = 736, 737, 738


def ask_ids(input_ids, max_new_tokens=64):
    idx = torch.tensor([input_ids], dtype=torch.long)
    out = model.generate(idx, max_new_tokens=max_new_tokens, eos_id=END)
    gen = out[0].tolist()
    resp = gen[len(input_ids):]
    return gen, resp


def ask(text, max_new_tokens=64):
    ids = [USER] + encode(text) + [ASSISTANT]
    gen, resp = ask_ids(ids, max_new_tokens)
    return resp, decode(resp)


if __name__ == '__main__':
    import json
    prompts = json.load(open('prompts.json'))
    results = {}
    for req in prompts['requests']:
        gen, resp = ask_ids(req['input_ids'])
        results[req['id']] = resp
        print(req['id'])
        print('  prompt:', decode(req['input_ids']))
        print('  full  :', decode_with_special(gen))
        print('  resp  :', decode(resp))
        print('  resp_ids:', resp)
    json.dump(results, open('results.json', 'w'))
