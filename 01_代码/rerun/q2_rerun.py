"""Q2 rerun with more fractions, uniform M=2000."""
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from solve_all import estimate_q2_shared

# Original 4 + 7 intermediate = 11 points
fracs = [0.005, 0.0055, 0.006, 0.0065, 0.007, 0.0075, 0.008, 0.0085, 0.009, 0.0095, 0.010]
M = 2000
SEED = 20260823

results = estimate_q2_shared(fracs, M, SEED)

for r in results:
    print(f"  {r['fraction']*100:.2f}%  N={r['n_a']}  p={r['probability']:.4f}  WL={r['wilson95_low']:.4f}  WH={r['wilson95_high']:.4f}")

out_path = str(ROOT) + '/02_论文/files/q2_probability.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\nSaved {len(results)} entries to {out_path}")
