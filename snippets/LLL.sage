m = previous_prime(2 ^ 32)
print("m", m)
a = randint(2, m)
s = randint(0, m)
X = [a ^ (i + 1) * s % m for i in range(4)]
print("X", X)
HIGH = [x - x % 2 ^ 16 for x in X]  # high 16 bits of X
print("HIGH", HIGH)
LOW = [x % 2 ^ 16 for x in X]  # low 16 bits of X (secret)
print("LOW ", LOW)

L = matrix([
    [m, 0, 0, 0], 
    [a ^ 1, -1, 0, 0], 
    [a ^ 2, 0, -1, 0], 
    [a ^ 3, 0, 0, -1]
])
print("L", L)

B = L.LLL()
print("B", B)

B_HIGH = B * vector(HIGH)
print("B_HIGH", B_HIGH)

B_LOW = vector([round(RR(b_high) / m) * m - b_high for b_high in B_HIGH])
print("B_LOW", B_LOW)

LOW_ = list(B.solve_right(B_LOW))
print(LOW_)
print(LOW)
