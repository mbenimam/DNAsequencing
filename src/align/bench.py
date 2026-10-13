"""Benchmark: one subprocess per (method, instance), so each run has its own peak memory."""
import csv
import glob
import os
import re
import subprocess
import sys

METHODS = ["naive", "table", "two-rows", "align-table", "align-hirschberg"]
MEMORY_LIMIT = 6 * 1024 ** 3  # address space allowed to one run, in bytes

_CHILD = r"""
import resource, sys, time
resource.setrlimit(resource.RLIMIT_AS, ({limit}, {limit}))
from align import read_instance, dist_naive, dist_table, dist_two_rows, align_dp, align_hirschberg, alignment_cost
x, y = read_instance(sys.argv[2])
method = sys.argv[1]
t = time.perf_counter()
if method == "naive": d = dist_naive(x, y)
elif method == "table": d = dist_table(x, y)[len(x)][len(y)]
elif method == "two-rows": d = dist_two_rows(x, y)
elif method == "align-table": d = align_dp(x, y)[0]
else: d = alignment_cost(*align_hirschberg(x, y))
t = time.perf_counter() - t
print(d, t, resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
"""


def _one(method, path, budget):
    """Return (status, distance, seconds, peak_kib) for one run."""
    code = _CHILD.format(limit=MEMORY_LIMIT)
    try:
        r = subprocess.run([sys.executable, "-c", code, method, path], capture_output=True, text=True, timeout=budget)
    except subprocess.TimeoutExpired:
        return "timeout", "", "", ""
    if r.returncode != 0:
        return ("memory" if "MemoryError" in r.stderr else "error"), "", "", ""
    d, t, rss = r.stdout.split()
    return "ok", int(d), float(t), int(rss)


def run(data, budget, out, plot):
    files = sorted(glob.glob(os.path.join(data, "Inst_*.adn")))
    os.makedirs(out, exist_ok=True)
    rows, stopped = [], set()
    for path in files:
        n = int(re.search(r"Inst_(\d+)_", path).group(1))
        for method in METHODS:
            if method in stopped:
                continue
            status, d, t, rss = _one(method, path, budget)
            rows.append({"instance": os.path.basename(path), "n": n, "method": method, "status": status,
                         "distance": d, "seconds": f"{t:.4f}" if status == "ok" else "", "peak_kib": rss})
            print(f"{n:>7} {method:<17} {status:<8} {d!s:>7} {(f'{t:.3f} s' if status == 'ok' else ''):>10} "
                  f"{(f'{rss / 1024:.0f} MiB' if status == 'ok' else ''):>9}", flush=True)
            if status != "ok":
                stopped.add(method)  # larger instances would fail the same way
    csv_path = os.path.join(out, "results.csv")
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print("written:", csv_path)
    if plot:
        _plot(rows, out)
    return 0


def _plot(rows, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    for method in METHODS:
        best = {}
        for r in rows:
            if r["method"] == method and r["status"] == "ok":
                cur = best.get(r["n"])
                t, m = float(r["seconds"]), r["peak_kib"] / 1024
                best[r["n"]] = (t, m) if cur is None else (min(cur[0], t), max(cur[1], m))
        ns = sorted(best)
        if not ns:
            continue
        axes[0].plot(ns, [best[n][0] for n in ns], marker="o", label=method)
        axes[1].plot(ns, [best[n][1] for n in ns], marker="o", label=method)
    for ax, label in zip(axes, ("time (s)", "peak memory of the process (MiB)")):
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_xlabel("length of the first sequence"); ax.set_ylabel(label)
        ax.grid(True, which="both", alpha=0.3); ax.legend()
    fig.tight_layout()
    path = os.path.join(out, "curves.png")
    fig.savefig(path, dpi=130)
    print("written:", path)
