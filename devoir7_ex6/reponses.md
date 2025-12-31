Exercice 6 — Hachage

1) H_pub(47572947294858218452) = 283005.
   Taille approx. des hash: log2(327680) ≈ 18.32 bits (~18 bits).

2) Collisions (brute force, deux entrées distinctes par h_i):
   - h1 = 118290: x = 31133 et x = 96669
   - h2 = 215350: x = 6865 et x = 72401
   - h3 = 311620: x = 21079 et x = 86615
   - h4 = 118975: x = 22238 et x = 87774
   - h5 = 54830:  x = 24745 et x = 90281

3) Pourquoi la fonction est cassée + collisions sans brute force:
   H_pub(x) = (A x + B) mod m est linéaire. Avec A = 1103515245, B = 12345, m = 327680,
   d = gcd(A, m) = 5. Chaque hash a 5 préimages (si (h - B) multiple de d).
   On résout A x ≡ (h - B) (mod m):
     A' = A / d, m' = m / d
     x0 = A'^{-1} * ((h - B)/d) (mod m')
     Solutions: x = x0 + k * m' pour k = 0..d-1.
   Cela redonne les collisions ci-dessus sans brute force.
