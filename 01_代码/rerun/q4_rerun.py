"""Q4 rerun: finer grid, M=200 per config."""
import sys
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
from solve_all import estimate, L, VA, VB

TRIALS = 200
SEED = 42
candidates = []

# fa: 0 to 1.0% step 0.1% (11 values)
# fb: 0 to 1.6% step 0.2% (9 values)
fa_grid = np.arange(0, 0.0101, 0.001)   # 0, 0.001, ..., 0.010
fb_grid = np.arange(0, 0.0161, 0.002)   # 0, 0.002, ..., 0.016

total = 0
for fa in fa_grid:
    for fb in fb_grid:
        na = int(round(fa * L**3 / VA))
        nb = int(round(fb * L**3 / VB))
        if na + nb == 0:
            continue
        total += 1

print(f"Total configurations: {total}, trials each: {TRIALS}")
print(f"Estimated total trials: {total * TRIALS}")

t0 = time.time()
idx = 0
for fa in fa_grid:
    for fb in fb_grid:
        na = int(round(fa * L**3 / VA))
        nb = int(round(fb * L**3 / VB))
        if na + nb == 0:
            continue
        idx += 1
        cost = 1.05 * na * VA / 1e9 + 0.05 * nb * VB / 1e9
        r = estimate(na, nb, TRIALS, SEED + na + 7 * nb)
        r.update({"fraction_a": float(fa), "fraction_b": float(fb), "cost": cost})
        candidates.append(r)
        if idx % 10 == 0:
            elapsed = time.time() - t0
            rate = idx / elapsed
            eta = (total - idx) / rate if rate > 0 else 0
            print(f"  [{idx}/{total}] fa={fa:.4f} fb={fb:.4f} na={na} nb={nb} "
                  f"p={r['probability']:.3f} cost={cost:.2f} "
                  f"({elapsed:.0f}s elapsed, ~{eta:.0f}s remaining)")

elapsed = time.time() - t0
print(f"\nDone in {elapsed:.1f}s")

# Summary
feasible = [x for x in candidates if x["probability"] >= 0.90]
feasible.sort(key=lambda x: x["cost"])
print(f"\nFeasible (p>=0.90): {len(feasible)} / {len(candidates)}")
print("\nTop 10 lowest cost feasible:")
for i, d in enumerate(feasible[:10]):
    print(f"  {i+1}. fa={d['fraction_a']:.4f} fb={d['fraction_b']:.4f} "
          f"na={d['n_a']} nb={d['n_b']} p={d['probability']:.4f} "
          f"cost={d['cost']:.4f} trials={d['trials']}")

# Save
out_path = str(ROOT) + '/02_论文/files/q4_mixture_search.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(candidates, f, ensure_ascii=False, indent=2)
print(f"\nSaved {len(candidates)} candidates to {out_path}")
