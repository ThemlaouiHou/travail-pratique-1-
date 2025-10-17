import sys
from collections import Counter, defaultdict
import math, re

# --- alphabet ---
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ "
M = len(ALPHABET)
IDX = {c:i for i,c in enumerate(ALPHABET)}
REV  = {i:c for i,c in enumerate(ALPHABET)}

# --- fréquences françaises approximatives pour A..Z, espace en dernier ---
# valeurs normalisées somma = 1 ; espace ~ 0.18 (approx.)
FREQ_FR = {
 'A':0.0812,'B':0.0090,'C':0.0326,'D':0.0367,'E':0.1470,'F':0.0107,'G':0.0087,'H':0.0074,
 'I':0.0754,'J':0.0061,'K':0.0005,'L':0.0546,'M':0.0301,'N':0.0713,'O':0.0574,'P':0.0252,
 'Q':0.0136,'R':0.0660,'S':0.0794,'T':0.0724,'U':0.0630,'V':0.0160,'W':0.0007,'X':0.0043,
 'Y':0.0039,'Z':0.0034, ' ':0.1498  # espace ajusté pour que la somme ≈1
}
# Normaliser (au cas où)
total = sum(FREQ_FR.values())
for k in FREQ_FR:
    FREQ_FR[k] /= total

# ---------------- utilitaires ----------------
def read_cipher(path):
    s = open(path, "r", encoding="utf-8").read().upper()
    s = re.sub(r'[^A-Z ]', '', s)    # garder seulement A-Z et espace
    return s

def ic_index(cipher):
    N = len(cipher)
    freqs = Counter(cipher)
    if N < 2: return 0.0
    ic = sum(v*(v-1) for v in freqs.values()) / (N*(N-1))
    return ic

# Kasiski: recherche de répétitions de n-grammes et collecte de leurs distances
def kasiski(cipher, min_n=3, max_n=5):
    distances = []
    for n in range(min_n, max_n+1):
        seen = {}
        for i in range(len(cipher)-n+1):
            chunk = cipher[i:i+n]
            if chunk in seen:
                distances.append(i - seen[chunk])
            else:
                seen[chunk] = i
    # factorisation brute des distances (petits facteurs seulement)
    def factors(x):
        fs=[]
        for f in range(2, 40):
            if x % f == 0:
                fs.append(f)
        return fs
    counter = Counter()
    for d in distances:
        for f in factors(d):
            counter[f]+=1
    return counter.most_common(20)

# découpe en colonnes modulo k
def column(cipher, k, r):
    return [cipher[i] for i in range(r, len(cipher), k)]

# méthode 'spaces' : pour une colonne, tester tous les shifts et prendre celui qui maximise espaces
def best_shift_by_spaces(chars):
    best_s = None
    best_spaces = -1
    for s in range(M):
        decoded = [(IDX[c]-s) % M for c in chars]
        spaces = sum(1 for v in decoded if REV[v] == ' ')
        if spaces > best_spaces:
            best_spaces = spaces
            best_s = s
    return best_s, best_spaces

# méthode chi2 : pour une colonne, choisir shift qui minimise le chi2 par rapport à FREQ_FR
def best_shift_by_chi2(chars):
    N = len(chars)
    best_s = None
    best_chi2 = float('inf')
    for s in range(M):
        # construire histogramme observé après shift
        obs = Counter()
        for c in chars:
            p = REV[(IDX[c]-s) % M]
            obs[p] += 1
        chi2 = 0.0
        for ch in ALPHABET:
            O = obs.get(ch, 0)
            E = FREQ_FR.get(ch, 0) * N
            # éviter division par zero
            if E > 0:
                chi2 += (O - E)**2 / E
        if chi2 < best_chi2:
            best_chi2 = chi2
            best_s = s
    return best_s, best_chi2

def recover_key(cipher, k, method='spaces'):
    shifts = []
    score_total = 0.0
    diagnostics = []
    for r in range(k):
        chars = column(cipher, k, r)
        if method == 'spaces':
            s, sc = best_shift_by_spaces(chars)
            shifts.append(s)
            score_total += sc
            diagnostics.append((r, s, sc))
        else:
            s, chi2 = best_shift_by_chi2(chars)
            shifts.append(s)
            score_total += -chi2   # on stocke -chi2 comme "score" (plus grand = mieux)
            diagnostics.append((r, s, chi2))
    return shifts, score_total, diagnostics

def shifts_to_key(shifts):
    return ''.join(REV[s] for s in shifts)

def decrypt_with_shifts(cipher, shifts):
    k = len(shifts)
    out_chars = []
    for i,c in enumerate(cipher):
        s = shifts[i % k]
        p = (IDX[c] - s) % M
        out_chars.append(REV[p])
    return ''.join(out_chars)

# ------------ pipeline --------------
def main(path):
    cipher = read_cipher(path)
    N = len(cipher)
    log = []
    log.append(f"Len cipher (cleaned) = {N}")
    ic = ic_index(cipher)
    log.append(f"IC (friedman) = {ic:.5f}")
    log.append("Kasiski factors (top 12): " + str(kasiski(cipher,3,5)[:12]))
    # tester k 1..20
    candidates = []
    log.append("\nTesting k=1..20 (spaces method & chi2 method)")
    for k in range(1,21):
        shifts_s, score_s, diag_s = recover_key(cipher, k, method='spaces')
        shifts_c, score_c, diag_c = recover_key(cipher, k, method='chi2')
        key_s = shifts_to_key(shifts_s)
        key_c = shifts_to_key(shifts_c)
        candidates.append((k, score_s, key_s, score_c, key_c))
        log.append(f"k={k:2d}  spaces_score={int(score_s):5d} key_spaces={key_s}   chi2_score={-score_c:.1f} key_chi2={key_c}")
    # choisir k par meilleur spaces_score
    best_by_spaces = max(candidates, key=lambda x: x[1])
    best_by_chi2   = max(candidates, key=lambda x: x[3])
    k_s, _, key_s, _, _ = best_by_spaces
    k_c, _, _, _, key_c = best_by_chi2
    log.append("\nBest by spaces: k=%d key=%s" % (k_s, key_s))
    log.append("Best by chi2  : k=%d key=%s" % (k_c, key_c))
    # Déchiffrer avec ces deux clés
    shifts_s, _, _ = recover_key(cipher, k_s, method='spaces')
    shifts_c, _, _ = recover_key(cipher, k_c, method='chi2')
    plain_s = decrypt_with_shifts(cipher, shifts_s)
    plain_c = decrypt_with_shifts(cipher, shifts_c)
    # sauvegarde
    open("vigenere_dechiffre_by_spaces.txt","w",encoding="utf-8").write(plain_s)
    open("vigenere_dechiffre_by_chi2.txt","w",encoding="utf-8").write(plain_c)
    open("vigenere_diagnostics.txt","w",encoding="utf-8").write("\n".join(log))
    print("DONE. Files:")
    print(" - vigenere_dechiffre_by_spaces.txt")
    print(" - vigenere_dechiffre_by_chi2.txt")
    print(" - vigenere_diagnostics.txt")
    print("\nSummary (diagnostics):\n")
    print("\n".join(log[:20]))
    print("\nBest by spaces: k=%d key=%s" % (k_s, key_s))
    print("Best by chi2  : k=%d key=%s" % (k_c, key_c))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python vigenere_pipeline.py vigenere.txt")
        sys.exit(1)
    main(sys.argv[1])
