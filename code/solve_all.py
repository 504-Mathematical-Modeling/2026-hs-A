"""Reproducible solver for 2026 Huashu Cup A.

The script uses periodic minimum-image geometry and union-find connectivity.
Run from the project root: python code/solve_all.py --mode all
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import openpyxl

L = 10000.0
HALF = L / 2
D0 = 1.8
RA = 30.0
HA = 5000.0
RB = 200.0
VA = np.pi * RA**2 * HA
VB = 4.0 * np.pi * RB**3 / 3.0


class DSU:
    def __init__(self, n: int):
        self.p = np.arange(n)

    def find(self, x: int) -> int:
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a: int, b: int) -> None:
        a, b = self.find(a), self.find(b)
        if a != b:
            self.p[b] = a


def min_image(x: np.ndarray) -> np.ndarray:
    return x - L * np.round(x / L)


def segment_segment_distance(a0, a1, b0, b1) -> float:
    """Distance between two 3-D segments after unwrapping b near a."""
    u = a1 - a0
    v = b1 - b0
    w = b0 - a0
    b = float(np.dot(u, v))
    c = float(np.dot(v, v))
    d = float(np.dot(u, w))
    e = float(np.dot(v, w))
    aa = float(np.dot(u, u))
    den = aa * c - b * b
    s, t = 0.0, 0.0
    if den > 1e-15:
        s = np.clip((b * e - c * d) / den, 0.0, 1.0)
    tnom = b * s + e
    if tnom < 0:
        t = 0.0
        s = np.clip(-d / aa, 0.0, 1.0) if aa > 0 else 0.0
    elif tnom > c:
        t = 1.0
        s = np.clip((b - d) / aa, 0.0, 1.0) if aa > 0 else 0.0
    else:
        t = tnom / c if c > 0 else 0.0
    return float(np.linalg.norm(w + s * u - t * v))


def capsule_distance(a0, a1, b0, b1, ra, rb) -> float:
    am = (a0 + a1) / 2
    bm = (b0 + b1) / 2
    shift = L * np.round((am - bm) / L)
    return max(0.0, segment_segment_distance(a0, a1, b0 + shift, b1 + shift) - ra - rb)


def segment_segment_distances(a0: np.ndarray, a1: np.ndarray,
                              b0: np.ndarray, b1: np.ndarray) -> np.ndarray:
    """Vectorized segment distances for arrays of paired segments."""
    u, v, w = a1 - a0, b1 - b0, b0 - a0
    aa = np.einsum("ij,ij->i", u, u)
    c = np.einsum("ij,ij->i", v, v)
    b = np.einsum("ij,ij->i", u, v)
    d = np.einsum("ij,ij->i", u, w)
    e = np.einsum("ij,ij->i", v, w)
    den = aa * c - b * b
    s = np.divide(b * e - c * d, den, out=np.zeros_like(den), where=den > 1e-15)
    s = np.clip(s, 0.0, 1.0)
    tnom = b * s + e
    t = np.divide(tnom, c, out=np.zeros_like(tnom), where=c > 1e-15)
    low = tnom < 0
    high = tnom > c
    t[low] = 0.0
    t[high] = 1.0
    s[low] = np.clip(np.divide(-d[low], aa[low], out=np.zeros_like(d[low]), where=aa[low] > 0), 0, 1)
    s[high] = np.clip(np.divide(b[high] - d[high], aa[high], out=np.zeros_like(d[high]), where=aa[high] > 0), 0, 1)
    return np.linalg.norm(w + s[:, None] * u - t[:, None] * v, axis=1)


def line_face_distance(p0, p1, face: float) -> float:
    # Distance from a segment to a plane perpendicular to X.
    x0, x1 = p0[0], p1[0]
    if (x0 - face) * (x1 - face) <= 0:
        return 0.0
    return min(abs(x0 - face), abs(x1 - face))


def build_graph(rods: np.ndarray, spheres: np.ndarray | None = None,
                d0: float = D0) -> tuple[bool, list[int]]:
    """Return conductivity and one shortest boundary-to-boundary path."""
    spheres = np.empty((0, 4)) if spheres is None else spheres
    na, nb = len(rods), len(spheres)
    n = na + nb + 2
    left, right = na + nb, na + nb + 1
    dsu = DSU(n)
    adj = [[] for _ in range(n)]

    def link(i: int, j: int) -> None:
        dsu.union(i, j)
        adj[i].append(j)
        adj[j].append(i)

    for i, (a0, a1) in enumerate(rods):
        if line_face_distance(a0, a1, -HALF) - RA <= d0:
            link(i, left)
        if line_face_distance(a0, a1, HALF) - RA <= d0:
            link(i, right)
    for j, row in enumerate(spheres):
        c = row[:3]
        r = row[3]
        if abs(c[0] + HALF) - r <= d0:
            link(na + j, left)
        if abs(c[0] - HALF) - r <= d0:
            link(na + j, right)

    if na > 1:
        ii, jj = np.triu_indices(na, 1)
        a0, a1 = rods[ii, 0], rods[ii, 1]
        b0, b1 = rods[jj, 0], rods[jj, 1]
        shift = L * np.round(((b0 + b1) / 2 - (a0 + a1) / 2) / L)
        dist = segment_segment_distances(a0, a1, b0 - shift, b1 - shift) - 2 * RA
        for i, j in zip(ii[dist <= d0], jj[dist <= d0]):
            link(int(i), int(j))
    if na and nb:
        ii, jj = np.meshgrid(np.arange(na), np.arange(nb), indexing="ij")
        a0, a1 = rods[ii.ravel(), 0], rods[ii.ravel(), 1]
        c = spheres[jj.ravel(), :3]
        shift = L * np.round(((a0 + a1) / 2 - c) / L)
        dvec = a1 - a0
        t = np.clip(np.einsum("ij,ij->i", c + shift - a0, dvec) /
                     np.einsum("ij,ij->i", dvec, dvec), 0, 1)
        dist = np.linalg.norm(a0 + t[:, None] * dvec - (c + shift), axis=1) - RA - RB
        for i, j in zip(ii.ravel()[dist <= d0], jj.ravel()[dist <= d0]):
            link(int(i), na + int(j))
    if nb > 1:
        ii, jj = np.triu_indices(nb, 1)
        dist = np.linalg.norm(min_image(spheres[ii, :3] - spheres[jj, :3]), axis=1) - 2 * RB
        for i, j in zip(ii[dist <= d0], jj[dist <= d0]):
            link(na + int(i), na + int(j))

    conductive = dsu.find(left) == dsu.find(right)
    if not conductive:
        return False, []
    prev = {left: None}
    q = [left]
    while q:
        u = q.pop(0)
        if u == right:
            break
        for v in adj[u]:
            if v not in prev:
                prev[v] = u
                q.append(v)
    path = []
    u = right
    while u is not None and u in prev:
        path.append(u)
        u = prev[u]
    return True, path[::-1]


def read_attachment(path: Path) -> list[np.ndarray]:
    wb = openpyxl.load_workbook(path, data_only=True)
    groups = []
    for ws in wb.worksheets:
        rows = []
        for row in ws.iter_rows(min_row=3, values_only=True):
            if row[0] is None:
                continue
            rows.append([[float(x) for x in row[:3]], [float(x) for x in row[3:6]]])
        groups.append(np.asarray(rows, dtype=float))
    return groups


def random_rods(n: int, rng: np.random.Generator) -> np.ndarray:
    centers = rng.uniform(-HALF, HALF, size=(n, 3))
    axes = rng.normal(size=(n, 3))
    axes /= np.linalg.norm(axes, axis=1, keepdims=True)
    return np.stack([centers - axes * HA / 2, centers + axes * HA / 2], axis=1)


def random_spheres(n: int, rng: np.random.Generator) -> np.ndarray:
    return np.column_stack([rng.uniform(-HALF, HALF, size=(n, 3)), np.full(n, RB)])


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return 0.0, 0.0
    p = k / n
    den = 1 + z*z/n
    ctr = (p + z*z/(2*n)) / den
    rad = z*np.sqrt(p*(1-p)/n + z*z/(4*n*n)) / den
    return max(0.0, ctr-rad), min(1.0, ctr+rad)


def estimate(na: int, nb: int, trials: int, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    hits = 0
    for _ in range(trials):
        ok, _ = build_graph(random_rods(na, rng), random_spheres(nb, rng))
        hits += int(ok)
    lo, hi = wilson(hits, trials)
    return {"n_a": na, "n_b": nb, "trials": trials, "hits": hits,
            "probability": hits / trials, "wilson95_low": lo, "wilson95_high": hi}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["all", "q1", "q2", "q3", "q4"], default="all")
    ap.add_argument("--trials", type=int, default=120)
    ap.add_argument("--seed", type=int, default=20260823)
    ap.add_argument("--attachment", type=Path, default=Path("00_题目与数据/附件.xlsx"))
    ap.add_argument("--out", type=Path, default=Path("results"))
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    (Path("figures")).mkdir(parents=True, exist_ok=True)
    groups = read_attachment(args.attachment)
    summary = {"constants": {"L_nm": L, "V_A_nm3": VA, "V_B_nm3": VB, "d0_nm": D0}}

    if args.mode in ("all", "q1"):
        rows = []
        for idx, rods in enumerate(groups, 1):
            ok, path = build_graph(rods)
            rows.append({"group": idx, "n_a": len(rods), "conductive": ok, "path_nodes": len(path)})
        import csv
        with (args.out / "q1_deterministic.csv").open("w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
        summary["q1"] = rows

    if args.mode in ("all", "q2", "q3"):
        fracs = [0.005, 0.006, 0.007, 0.010]
        q2 = []
        for i, frac in enumerate(fracs):
            n = int(round(frac * L**3 / VA))
            q2.append({"fraction": frac, **estimate(n, 0, args.trials, args.seed + i)})
        (args.out / "q2_probability.json").write_text(json.dumps(q2, ensure_ascii=False, indent=2), encoding="utf-8")
        summary["q2"] = q2
        xs = np.array([x["fraction"]*100 for x in q2]); ys = np.array([x["probability"] for x in q2])
        plt.figure(figsize=(5.5, 3.5)); plt.plot(xs, ys, "o-"); plt.axhline(.9, ls="--", color="gray")
        plt.xlabel("A 体积分数 (%)"); plt.ylabel("导通概率"); plt.tight_layout(); plt.savefig("figures/q2_probability.pdf"); plt.close()
        grid = np.linspace(.005, .03, 13); q3 = []
        for i, frac in enumerate(grid):
            n = int(round(frac * L**3 / VA)); q3.append({"fraction": float(frac), **estimate(n, 0, max(20, args.trials//2), args.seed+100+i)})
        feasible = [x for x in q3 if x["probability"] >= .9]
        summary["q3"] = feasible[0] if feasible else None
        (args.out / "q3_threshold.json").write_text(json.dumps(q3, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.mode in ("all", "q4"):
        candidates = []
        for fa in np.arange(0, .0101, .002):
            for fb in np.arange(0, .0201, .004):
                na, nb = int(round(fa*L**3/VA)), int(round(fb*L**3/VB))
                if na + nb == 0: continue
                r = estimate(na, nb, max(12, args.trials//4), args.seed + na + 7*nb)
                r.update({"fraction_a": float(fa), "fraction_b": float(fb),
                          "cost": 1.05*na*VA/1e9 + .05*nb*VB/1e9})
                candidates.append(r)
        feasible = [x for x in candidates if x["probability"] >= .9]
        feasible.sort(key=lambda x: x["cost"])
        summary["q4"] = feasible[:10]
        (args.out / "q4_mixture_search.json").write_text(json.dumps(candidates, ensure_ascii=False, indent=2), encoding="utf-8")
    (args.out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
