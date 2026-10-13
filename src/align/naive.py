"""Edit distance by enumerating every alignment. Exponential: for tiny inputs only."""
import sys

from .costs import C_DEL, C_INS, sub_cost


def dist_naive(x, y):
    """Edit distance from x to y, by trying every alignment."""
    sys.setrecursionlimit(max(sys.getrecursionlimit(), len(x) + len(y) + 100))
    return _explore(x, y, 0, 0, 0, float("inf"))


def _explore(x, y, i, j, cost, best):
    """Extend a partial alignment of (x[:i], y[:j]) of the given cost in every way.

    Returns the cost of the best complete alignment known after the call.
    """
    if i == len(x) and j == len(y):
        return cost if cost < best else best
    if i < len(x) and j < len(y):
        best = _explore(x, y, i + 1, j + 1, cost + sub_cost(x[i], y[j]), best)
    if i < len(x):
        best = _explore(x, y, i + 1, j, cost + C_DEL, best)
    if j < len(y):
        best = _explore(x, y, i, j + 1, cost + C_INS, best)
    return best
