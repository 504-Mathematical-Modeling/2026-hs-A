"""Q3 bisection with uniform M=2000."""
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from solve_all import estimate, L, VA
import numpy as np

M = 2000
SEED = 20260823
THRESH = 0.90

def frac_to_n(f):
    return int(round(f * L**3 / VA))

results = []

# Phase 1: coarse scan 0.85% to 1.30%, step 0.05%
print("=== Phase 1: Coarse scan ===")
coarse = np.arange(0.0085, 0.01301, 0.0005)
for i, frac in enumerate(coarse):
    n = frac_to_n(frac)
    r = estimate(n, 0, M, SEED + i)
    r["fraction"] = float(frac)
    results.append(r)
    print(f"  {frac*100:.3f}%  N={n}  p={r['probability']:.4f}  WL={r['wilson95_low']:.4f}")

# Find crossing: first fraction where Wilson lower bound >= 0.90
cross_idx = None
for i, r in enumerate(results):
    if r["wilson95_low"] >= THRESH:
        cross_idx = i
        break

if cross_idx is None:
    print("ERROR: no crossing found in coarse scan")
    sys.exit(1)

lo_idx = max(0, cross_idx - 1)
hi_idx = cross_idx
print(f"\nCrossing between {results[lo_idx]['fraction']*100:.3f}% and {results[hi_idx]['fraction']*100:.3f}%")

# Phase 2: bisection within [lo, hi], precision 0.0001 (0.01%)
print("\n=== Phase 2: Bisection ===")
phi_lo = results[lo_idx]["fraction"]
phi_hi = results[hi_idx]["fraction"]
iter_count = 0
while phi_hi - phi_lo > 0.0001:
    phi_mid = (phi_lo + phi_hi) / 2
    n = frac_to_n(phi_mid)
    r = estimate(n, 0, M, SEED + 1000 + iter_count)
    r["fraction"] = float(phi_mid)
    results.append(r)
    print(f"  {phi_mid*100:.4f}%  N={n}  p={r['probability']:.4f}  WL={r['wilson95_low']:.4f}")
    if r["wilson95_low"] >= THRESH:
        phi_hi = phi_mid
    else:
        phi_lo = phi_mid
    iter_count += 1

print(f"\nFinal threshold: {phi_hi*100:.4f}%  N_A={frac_to_n(phi_hi)}")

# Save
out_path = str(ROOT) + '/02_论文/files/q3_threshold.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\nSaved {len(results)} entries to {out_path}")
