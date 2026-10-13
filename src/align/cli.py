"""Command line: align distance|align|bench."""
import argparse
import sys
import time

from . import (align_dp, align_hirschberg, alignment_cost, dist_naive, dist_table,
               dist_two_rows, read_instance)

DISTANCE = {
    "naive": dist_naive,
    "table": lambda x, y: dist_table(x, y)[len(x)][len(y)],
    "two-rows": dist_two_rows,
}
ALIGN = {
    "table": lambda x, y: align_dp(x, y)[1:],
    "hirschberg": align_hirschberg,
}


def _print_alignment(xbar, ybar, width=60):
    for k in range(0, len(xbar), width):
        a, b = xbar[k:k + width], ybar[k:k + width]
        print(a)
        print("".join("|" if p == q else " " for p, q in zip(a, b)))
        print(b)
        print()


def main(argv=None):
    p = argparse.ArgumentParser(prog="align", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("distance", help="edit distance between the two sequences of an instance file")
    d.add_argument("file")
    d.add_argument("--method", choices=DISTANCE, default="two-rows")
    a = sub.add_parser("align", help="print an optimal alignment")
    a.add_argument("file")
    a.add_argument("--method", choices=ALIGN, default="hirschberg")
    b = sub.add_parser("bench", help="time and memory of every method on the instance files")
    b.add_argument("--data", default="data")
    b.add_argument("--budget", type=float, default=60.0, help="seconds allowed per run")
    b.add_argument("--out", default="bench")
    b.add_argument("--plot", action="store_true", help="also draw the curves (needs matplotlib)")
    args = p.parse_args(argv)

    if args.cmd == "bench":
        from .bench import run
        return run(args.data, args.budget, args.out, args.plot)

    x, y = read_instance(args.file)
    start = time.perf_counter()
    if args.cmd == "distance":
        print(DISTANCE[args.method](x, y))
    else:
        xbar, ybar = ALIGN[args.method](x, y)
        _print_alignment(xbar, ybar)
        print(f"cost {alignment_cost(xbar, ybar)}, length {len(xbar)}")
    print(f"{args.method}: {time.perf_counter() - start:.3f} s", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
