import secrets
from typing import List, Tuple

# Utility method: rotate left 8 bits
def rotate8(x: int, n: int) -> int:
    x &= 0xFF
    return ((x << n) | (x >> (8 - n))) & 0xFF

def quarter_round(a: int, b: int, c: int, d: int) -> Tuple[int, int, int, int]:
    a = (a + b) & 0xFF
    d = rotate8(d ^ a, 1)
    c = (c + d) & 0xFF
    b = rotate8(b ^ c, 3)

    a = (a + b) & 0xFF
    d = rotate8(d ^ a, 5)
    c = (c + d) & 0xFF
    b = rotate8(b ^ c, 7)
    return a, b, c, d

def doubleround(state: List[int]) -> List[int]:
    s = state[:]
    # Columns
    s[0], s[4], s[8],  s[12] = quarter_round(s[0], s[4], s[8],  s[12])
    s[1], s[5], s[9],  s[13] = quarter_round(s[1], s[5], s[9],  s[13])
    s[2], s[6], s[10], s[14] = quarter_round(s[2], s[6], s[10], s[14])
    s[3], s[7], s[11], s[15] = quarter_round(s[3], s[7], s[11], s[15])
    # Diagonals
    s[0], s[5], s[10], s[15] = quarter_round(s[0], s[5], s[10], s[15])
    s[1], s[6], s[11], s[12] = quarter_round(s[1], s[6], s[11], s[12])
    s[2], s[7], s[8],  s[13] = quarter_round(s[2], s[7], s[8],  s[13])
    s[3], s[4], s[9],  s[14] = quarter_round(s[3], s[4], s[9],  s[14])
    return s

def mini_chacha_block(const4: bytes, key4: bytes, counter: int, nonce2: bytes, rounds: int = 5) -> bytes:
    # Duplicate key4 to form key8
    key8 = key4 + key4 

    # Initialize state
    s0 = [const4[0], const4[1], const4[2], const4[3]]
    s1 = [key8[0], key8[1], key8[2], key8[3]]
    s2 = [key8[4], key8[5], key8[6], key8[7]]
    cnt0 = counter & 0xFF
    cnt1 = (counter >> 8) & 0xFF
    s3 = [cnt0, cnt1, nonce2[0], nonce2[1]]

    state = s0 + s1 + s2 + s3
    init  = state[:]

    i = 0
    while i < rounds:
        state = doubleround(state)
        i += 1

    # Add initial state to final state
    result = []
    j = 0
    while j < 16:
        result.append((state[j] + init[j]) & 0xFF)
        j += 1
    return bytes(result)


class MiniChaCha:
    def __init__(self, const4_text: str, key4: bytes = None, nonce2: bytes = None, counter_start: int = 1):
        # Only take 4 chars
        c4 = (const4_text[:4]).encode("ascii", "strict")
        self.const4 = c4

        # key 32 bits
        if key4 is None:
            self.key4 = secrets.token_bytes(4)
        else:
            self.key4 = key4

        # nonce 16 bits
        if nonce2 is None:
            self.nonce2 = secrets.token_bytes(2)
        else:
            self.nonce2 = nonce2

        # counter 16 bits
        self.counter = counter_start & 0xFFFF

    def encrypt(self, plaintext: bytes) -> bytes:
        result = bytearray()
        needed = len(plaintext)

        while len(result) < needed:
            # Generate next block
            block = mini_chacha_block(self.const4, self.key4, self.counter, self.nonce2, rounds=5)
            # Increment counter modulo 2^16
            self.counter = (self.counter + 1) & 0xFFFF

            # How many bytes to take from this block
            need = needed - len(result)
            if need >= 16:
                ks_chunk = block
            else:
                ks_chunk = block[:need]

            # XOR and append
            start = len(result)
            for i in range(len(ks_chunk)):
                result.append(plaintext[start + i] ^ ks_chunk[i])
        return bytes(result)

    decrypt = encrypt

    def params(self):
        return {
            "const4": self.const4,
            "key4_hex": self.key4.hex(),
            "nonce2_hex": self.nonce2.hex(),
            "counter": self.counter
        }


##### MAIN
if __name__ == "__main__":

    # Ex2: part 1
    nom = "JEDD"
    mc1 = MiniChaCha(nom)
    print("Parameters :", mc1.params())

    # Ex2: part 2,3
    chanson = "Une souris verte qui courait dans l'herbe".encode("utf-8")
    c = mc1.encrypt(chanson)
    mc2 = MiniChaCha(nom, key4=mc1.key4, nonce2=mc1.nonce2, counter_start=1)
    r = mc2.decrypt(c)

    print("Base : ", chanson)
    print("Cipher:", c.hex())
    print("Decrypt:", r)
