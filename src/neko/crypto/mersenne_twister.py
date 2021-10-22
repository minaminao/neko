A = 0x9908b0df
B = 0x9D2C5680
C = 0xEFC60000
U = 11
S = 7
T = 15
L = 18
M = 397
N = 624
W = 32
UPPER_MASK = 0x80000000 # most significant W-R=1 bits
LOWER_MASK = 0x7fffffff

def inv_rightshift_xor(x, shift):
    i = 1
    y = x
    while i * shift < W:
        z = y >> shift
        y = x ^ z
        i += 1
    return y

def inv_leftshift_xor(x, shift, mask):
    i = 1
    y = x
    while i * shift < W:
        z = y << shift
        y = x ^ (z & mask)
        i += 1
    return y

def untemper(x: int) -> int:
    x = inv_rightshift_xor(x, L)
    x = inv_leftshift_xor(x, T, C)
    x = inv_leftshift_xor(x, S, B)
    x = inv_rightshift_xor(x, U)
    return x

def calc_prev_state(state: tuple) -> tuple:
    """
    前のステートを計算
    """
    state = list(state)
    for i in range(N - 1, -1, -1):
        x = state[i] ^ state[(i + M) % N]
        if (x & UPPER_MASK) == UPPER_MASK:
            x ^= A
        x = (x << 1) & UPPER_MASK
        y = state[(i - 1 + N) % N] ^ state[(i - 1 + M) % N]
        if (y & UPPER_MASK) == UPPER_MASK:
            y ^= A
            x |= 1
        y = (y << 1) & LOWER_MASK
        state[i] = x | y
    return tuple(state)

