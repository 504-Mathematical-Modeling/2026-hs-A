"""Verify all paper table numbers against JSON data files."""
import json
import re

BASE = '/home/gsh/2026-hs-A'

q2 = json.load(open(f'{BASE}/02_论文/files/q2_probability.json'))
q3 = json.load(open(f'{BASE}/02_论文/files/q3_threshold.json'))
q4 = json.load(open(f'{BASE}/02_论文/files/q4_mixture_search.json'))

def wilson(k, n, z=1.96):
    p = k / n
    den = 1 + z*z/n
    ctr = (p + z*z/(2*n)) / den
    rad = z*(p*(1-p)/n + z*z/(4*n*n))**0.5 / den
    return max(0.0, ctr-rad), min(1.0, ctr+rad)

print("=== Q2 表7/附表A 核查 ===")
q2_by_frac = {round(d['fraction'], 4): d for d in q2}
# Values claimed in paper tables
claims_q2 = [
    (0.0050, 354, 629), (0.0055, 389, 766), (0.0060, 424, 895),
    (0.0065, 460, 1033), (0.0070, 495, 1165), (0.0075, 530, 1272),
    (0.0080, 566, 1386), (0.0085, 601, 1476), (0.0090, 636, 1579),
    (0.0095, 672, 1680), (0.0100, 707, 1746),
]
for frac, na_claim, k_claim in claims_q2:
    d = q2_by_frac.get(frac)
    if d is None:
        print(f"  phi={frac:.4f}: 不在JSON中!")
        continue
    ok_na = d['n_a'] == na_claim
    ok_k = d['hits'] == k_claim
    lo, hi = wilson(d['hits'], d['trials'])
    p = d['hits'] / d['trials']
    print(f"  phi={frac:.4f}: N_A {d['n_a']}({'OK' if ok_na else 'MISMATCH:'+str(na_claim)}) "
          f"hits {d['hits']}({'OK' if ok_k else 'MISMATCH:'+str(k_claim)}) p={p:.4f} "
          f"Wilson=[{lo:.4f},{hi:.4f}]")

print("\n=== Q3 表8 核查 ===")
q3_sorted = sorted(q3, key=lambda d: d['fraction'])
for d in q3_sorted:
    lo, hi = wilson(d['hits'], d['trials'])
    print(f"  phi={d['fraction']*100:.5f}%: N_A={d['n_a']} hits={d['hits']}/{d['trials']} "
          f"p={d['probability']:.4f} WL_json={d['wilson95_low']:.4f} WL_recalc={lo:.4f}")

print("\n=== Q4 候选表核查 ===")
q4_by_key = {(d['n_a'], d['n_b']): d for d in q4}
claims_q4 = [(0, 119), (0, 179), (71, 119), (283, 119), (566, 119)]
for na, nb in claims_q4:
    d = q4_by_key.get((na, nb))
    if d is None:
        print(f"  ({na},{nb}): 不在JSON中!")
        continue
    print(f"  ({na},{nb}): p={d['probability']:.4f} WL={d['wilson95_low']:.4f} cost={d['cost']:.4f}")

# Check: cheapest point-estimate-feasible vs cheapest Wilson-certified
print("\n=== Q4 最优方案判据对比 ===")
feas_pt = [d for d in q4 if d['probability'] >= 0.90]
feas_pt.sort(key=lambda x: x['cost'])
feas_wl = [d for d in q4 if d['wilson95_low'] >= 0.90]
feas_wl.sort(key=lambda x: x['cost'])
print(f"  点估计>=0.90 最便宜: ({feas_pt[0]['n_a']},{feas_pt[0]['n_b']}) cost={feas_pt[0]['cost']:.4f} p={feas_pt[0]['probability']:.4f}")
print(f"  Wilson下界>=0.90 最便宜: ({feas_wl[0]['n_a']},{feas_wl[0]['n_b']}) cost={feas_wl[0]['cost']:.4f} p={feas_wl[0]['probability']:.4f}")

# Mixed-only (na>0) cheapest under both criteria
mix_pt = [d for d in feas_pt if d['n_a'] > 0]
mix_wl = [d for d in feas_wl if d['n_a'] > 0]
print(f"  含A混合 点估计最便宜: ({mix_pt[0]['n_a']},{mix_pt[0]['n_b']}) cost={mix_pt[0]['cost']:.4f}")
print(f"  含A混合 Wilson最便宜: ({mix_wl[0]['n_a']},{mix_wl[0]['n_b']}) cost={mix_wl[0]['cost']:.4f}")

# Pure-A reference points in Q4 data
print("\n=== Q4 中纯A参考点 ===")
for d in q4:
    if d['n_b'] == 0 and d['fraction_a'] >= 0.008:
        print(f"  fa={d['fraction_a']*100:.1f}%: N_A={d['n_a']} p={d['probability']:.4f} WL={d['wilson95_low']:.4f} cost={d['cost']:.4f}")
