import struct

MASK = (1 << 64) - 1

def mix64(z):
    z &= MASK
    z ^= z >> 30
    z = (z * 0xbf58476d1ce4e5b9) & MASK
    z ^= z >> 27
    z = (z * 0x94d049bb133111eb) & MASK
    z ^= z >> 31
    return z

def rotl(x, n):
    n &= 63
    x &= MASK
    return ((x << n) | (x >> (64 - n))) & MASK

def rotr(x, n):
    n &= 63
    x &= MASK
    return ((x >> n) | (x << (64 - n))) & MASK

data = open("faultline.map", "rb").read()
fieldA, = struct.unpack_from("<H", data, 6)
pathlen, = struct.unpack_from("<H", data, 8)
b_c = data[12]
b_d = data[13]
seed, = struct.unpack_from("<Q", data, 14)

session_key = mix64(seed ^ 0x1bd11bdaa9fc1a22)
X0 = ((seed >> 8) & 0xf) ^ b_c
Y0 = ((seed >> 20) & 0xf) ^ b_d

roads_raw = data[78:]

r10c = 0xa0761d6478bd642f
r9c  = 0xe162582d6a382c8d
r8c  = 0xbf58476d1ce4e5b9
rdic = 0x94d049bb133111eb
r11c = 0x6a09e667f3bcc909
wyprime = 0xd6e8feb86659fd93

def decode_road(index):
    rec = roads_raw[index*24:(index+1)*24]
    chunks = [int.from_bytes(rec[i:i+8], 'little') for i in (0,8,16)]
    rsi = (index * wyprime) & MASK
    out = []
    rdx = 0
    for i in range(3):
        m0 = (seed ^ rdx ^ rsi ^ r11c) & MASK
        t1 = m0 ^ (m0 >> 30)
        t2 = (t1 * r8c) & MASK
        t3 = t2 ^ (t2 >> 27)
        t4 = (t3 * rdic) & MASK
        out_partial = chunks[i] ^ t4
        t5 = t4 >> 31
        final = (t5 ^ out_partial) & MASK
        out.append(final)
        rdx = (rdx + r10c) & MASK
    assert rdx == r9c
    decoded16 = out[0].to_bytes(8,'little') + out[1].to_bytes(8,'little')
    F0,F1,F2,F3,F4,F5 = decoded16[0:6]
    F67 = int.from_bytes(decoded16[6:8], 'little')
    K = int.from_bytes(decoded16[8:16], 'little')
    Q = out[2]
    return dict(F0=F0,F1=F1,F2=F2,F3=F3,F4=F4,F5=F5,F67=F67,K=K,Q=Q)

dx = [0, 1, 0, -1]
dy = [-1, 0, 1, 0]

x, y = X0, Y0
steps = []
for rnd in range(fieldA):
    index = y*16 + x
    rd = decode_road(index)
    dl = rd['F0']; F1=rd['F1']; F2=rd['F2']; F3=rd['F3']; F4=rd['F4']; F67=rd['F67']; K=rd['K']
    if dl == 0:
        R2 = F2 % 6
        if F1 == 0:
            R3 = F3 % 6
            steps.append(('A0', R2, R3, F4, K))
        else:
            odd_mult = ((((F67 * 0x1000000010000) & MASK) | ((F67 ^ 0xa55a) & 0xffff)) | 1) & MASK
            steps.append(('A1', R2, odd_mult, K))
    elif dl == 1:
        R2 = F2 % 6
        R3 = F3 % 6
        if F1 == 0:
            steps.append(('B0', R2, R3, F4 & 0x3f, K))
        else:
            steps.append(('B1', R2, R3, F4 & 0x3f, K))
    elif dl == 2:
        R2 = F2 % 6
        if F1 == 0:
            rot_amt = R2 % 5
            steps.append(('C0', rot_amt))
        else:
            steps.append(('C1', R2, F4, K))
    d = rd['F5'] & 3
    x, y = x + dx[d], y + dy[d]

def forward_rounds(state0):
    st = list(state0)
    for s in steps:
        if s[0]=='A0':
            _,R2,R3,F4,K = s
            st[R2] = (st[R2] + rotl(st[R3]^K, F4)) & MASK
        elif s[0]=='A1':
            _,R2,odd,K = s
            st[R2] = (odd * ((K + st[R2]) & MASK)) & MASK
        elif s[0]=='B0':
            _,R2,R3,rot,K = s
            oR2=st[R2]; oR3=st[R3]
            st[R2] = oR3
            st[R3] = oR2 ^ rotl((oR3+K)&MASK, rot)
        elif s[0]=='B1':
            _,R2,R3,rot,K = s
            st[R2] = st[R2] ^ rotl(st[R3]^K, rot)
        elif s[0]=='C0':
            _,rot_amt = s
            new_st=[None]*6
            for j in range(6):
                new_st[(rot_amt+j+1)%6]=st[j]
            st=new_st
        elif s[0]=='C1':
            _,R2,F4,K = s
            st[R2] = rotl(st[R2]^K, F4)
    return st

def backward_rounds(stateF):
    st = list(stateF)
    for s in reversed(steps):
        if s[0]=='A0':
            _,R2,R3,F4,K = s
            st[R2] = (st[R2] - rotl(st[R3]^K, F4)) & MASK
        elif s[0]=='A1':
            _,R2,odd,K = s
            inv = pow(odd,-1,1<<64)
            st[R2] = ((st[R2]*inv)&MASK) - K
            st[R2] &= MASK
        elif s[0]=='B0':
            _,R2,R3,rot,K = s
            nR2=st[R2]; nR3=st[R3]
            oR3=nR2
            oR2=nR3 ^ rotl((oR3+K)&MASK, rot)
            st[R2]=oR2; st[R3]=oR3
        elif s[0]=='B1':
            _,R2,R3,rot,K = s
            st[R2] = st[R2] ^ rotl(st[R3]^K, rot)
        elif s[0]=='C0':
            _,rot_amt = s
            old_st=[None]*6
            for j in range(6):
                old_st[j]=st[(rot_amt+j+1)%6]
            st=old_st
        elif s[0]=='C1':
            _,R2,F4,K = s
            st[R2] = rotr(st[R2],F4) ^ K
    return st

r10c2 = 0xbadc0ffee0ddf00d
mulA = 0xbf58476d1ce4e5b9
mulB = 0x94d049bb133111eb
incr = 0x9e3779b97f4a7c15

def whiten_forward(raw6):
    rdx=0
    out=[]
    for i in range(6):
        m0=(seed^rdx^r10c2)&MASK
        t1=m0^(m0>>30)
        t2=(t1*mulA)&MASK
        t3=t2^(t2>>27)
        t4=(t3*mulB)&MASK
        out_partial = raw6[i]^t4
        t5 = t4>>31
        final=(t5^out_partial)&MASK
        out.append(final)
        rdx=(rdx+incr)&MASK
    return out

def whiten_backward(out6):
    rdx=0
    raw=[]
    for i in range(6):
        m0=(seed^rdx^r10c2)&MASK
        t1=m0^(m0>>30)
        t2=(t1*mulA)&MASK
        t3=t2^(t2>>27)
        t4=(t3*mulB)&MASK
        final=out6[i]
        t5=t4>>31
        out_partial = final^t5
        raw_i = out_partial ^ t4
        raw.append(raw_i&MASK)
        rdx=(rdx+incr)&MASK
    return raw

def decode_header_secret():
    ciphertext = data[22:22+48]
    r10 = 0xe7037ed1a0b428db
    r9  = 0x243f6a8885a308d3
    r8  = 0xbf58476d1ce4e5b9
    rdi = 0x94d049bb133111eb
    final_key = 0x7180212ea001616a  # empirically-verified runtime key (stack-adjacent, input-independent)
    plain = bytearray(48)
    for i in range(48):
        block = i >> 3
        rcx = (block * r10) & MASK
        rcx ^= final_key
        rcx ^= r9
        rax = rcx
        rax ^= (rax >> 30)
        rax = (rax * r8) & MASK
        rax ^= (rax >> 27)
        rax = (rax * rdi) & MASK
        rax ^= (rax >> 31)
        shift = (i & 7) * 8
        kb = (rax >> shift) & 0xff
        plain[i] = ciphertext[i] ^ kb
    return bytes(plain)

target48 = decode_header_secret()
target_state = [int.from_bytes(target48[i*8:(i+1)*8],'little') for i in range(6)]

whitened_needed = backward_rounds(target_state)
raw_needed = whiten_backward(whitened_needed)
raw_bytes = b''.join(v.to_bytes(8,'little') for v in raw_needed)
print("REQUIRED RAW STATE BYTES:", raw_bytes.hex())
print(raw_bytes)
print("first42 (required argv):", raw_bytes[:42])
print("bytes42-47 (should be zero):", raw_bytes[42:48].hex())

chk = forward_rounds(whiten_forward(raw_needed))
print("verify == target:", chk == target_state)
