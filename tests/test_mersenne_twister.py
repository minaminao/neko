import os
import random
from neko.crypto.mersenne_twister import untemper, calc_prev_state, W, N, UPPER_MASK


def test_calc_prev_state():
    state_len = N * 4
    state0_bytes = os.urandom(state_len)
    # 32bitの整数列
    state0 = tuple(int.from_bytes(state0_bytes[i:i + 4], "big") for i in range(0, state_len, 4))
    # カウンターに(N,)を指定するとstateがアップデートされる
    random.setstate((3, state0 + (0, ), None))

    # P回ステートを変化させる
    P = 100
    for _ in range(P):
        outputs = [random.getrandbits(W) for _ in range(N)]

    # Recover
    last_state = tuple(list(map(untemper, outputs)))
    state0_ = last_state
    for _ in range(P - 1):
        state0_ = calc_prev_state(state0_)
    state0_bytes_ = b""
    for x in state0_:
        state0_bytes_ += x.to_bytes(4, "big")

    # 最初の要素は最上位ビットしか使わないし逆算できない
    assert state0[1:] == state0_[1:]
    assert (state0[0] & UPPER_MASK) == (state0_[0] & UPPER_MASK)
    assert state0_bytes[4:] == state0_bytes_[4:]
