import math
from collections import Counter

n = 1005658541636276696854926736111523240565378642222118817358603616124640001
g = 2
A = 694345273912301015795665084471934281997943951751938128184262171033972161
B = 45219809272265904064518788699770061112569516384310833106022960617800893

# Factorization from FactorDB (network lookup done separately).
p = 845722348837208875924502082373440001
q = 1189111938473620218791973405751200001

# Order of g=2 in Z_p* and Z_q* (computed by reducing p-1 and q-1).
ord_p = 84572234883720887592450208237344000
ord_q = 28826956084208975001017537109120

factors_p = Counter({3: 9, 2: 8, 31: 6, 19: 5, 11: 4, 5: 3, 7: 3, 23: 3})
factors_q = Counter({2: 7, 3: 6, 23: 5, 17: 5, 29: 5, 7: 3, 31: 2, 5: 1})


def dlog_prime_power(g_base, h_base, mod, order, prime, exp):
    n_i = prime ** exp
    m = order // n_i
    g1 = pow(g_base, m, mod)
    h1 = pow(h_base, m, mod)
    gk = pow(g1, prime ** (exp - 1), mod)  # order prime
    x = 0
    for k in range(exp):
        c = (h1 * pow(g1, -x, mod)) % mod
        c = pow(c, prime ** (exp - 1 - k), mod)
        d = None
        cur = 1
        for i in range(prime):
            if cur == c:
                d = i
                break
            cur = (cur * gk) % mod
        if d is None:
            raise ValueError("Discrete log failed for prime power")
        x += d * (prime ** k)
    return x


def pohlig_hellman(g_base, h_base, mod, order, factors):
    congruences = []
    for prime, exp in factors.items():
        x_i = dlog_prime_power(g_base, h_base, mod, order, prime, exp)
        congruences.append((x_i, prime ** exp))
    # CRT, pairwise coprime moduli
    x = 0
    N = 1
    for _, ni in congruences:
        N *= ni
    for ai, ni in congruences:
        Mi = N // ni
        inv = pow(Mi, -1, ni)
        x = (x + ai * Mi * inv) % N
    return x


def crt_general(a1, n1, a2, n2):
    g = math.gcd(n1, n2)
    if (a1 - a2) % g != 0:
        raise ValueError("No CRT solution")
    lcm = n1 // g * n2
    m1 = n1 // g
    m2 = n2 // g
    t = ((a2 - a1) // g) * pow(m1, -1, m2) % m2
    x = (a1 + n1 * t) % lcm
    return x, lcm


ap = pohlig_hellman(g % p, A % p, p, ord_p, factors_p)
aq = pohlig_hellman(g % q, A % q, q, ord_q, factors_q)

a, lcm_ord = crt_general(ap, ord_p, aq, ord_q)

k = pow(B, a, n)

print("ap =", ap)
print("aq =", aq)
print("a =", a)
print("lcm_ord =", lcm_ord)
print("check A:", pow(g, a, n) == A)
print("shared key k =", k)
