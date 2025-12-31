import math

A = 1103515245
B = 12345
m = 327680

x = 47572947294858218452
h = (A * x + B) % m
hash_bits = math.log2(m)

h_values = [118290, 215350, 311620, 118975, 54830]

# Brute force: find two inputs per target hash.
collisions = {h: [] for h in h_values}
candidate = 0
while any(len(v) < 2 for v in collisions.values()):
    hv = (A * candidate + B) % m
    if hv in collisions and len(collisions[hv]) < 2:
        collisions[hv].append(candidate)
    candidate += 1

# Non-brute-force: solve linear congruence.
d = math.gcd(A, m)
A1 = A // d
m1 = m // d

def egcd(a, b):
    if b == 0:
        return (a, 1, 0)
    g, x1, y1 = egcd(b, a % b)
    return (g, y1, x1 - (a // b) * y1)

g, inv, _ = egcd(A1, m1)
if g != 1:
    raise ValueError("No modular inverse")
inv %= m1

all_solutions = {}
for hv in h_values:
    rhs = (hv - B) % m
    if rhs % d != 0:
        all_solutions[hv] = []
        continue
    x0 = (inv * (rhs // d)) % m1
    all_solutions[hv] = [x0 + k * m1 for k in range(d)]

print("hash(x) =", h)
print("hash_bits =", hash_bits)
print("bruteforce_collisions =", collisions)
print("linear_solutions =", all_solutions)
