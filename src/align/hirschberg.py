"""An optimal alignment in linear memory, by divide and conquer (Hirschberg's idea).

Split x in the middle, find where an optimal alignment crosses that row of
the table, and solve the two halves independently.
"""
import sys

from .costs import C_DEL, C_INS, GAP, sub_cost, sub_rows


def cut(x, y):
    """Column where an optimal alignment of (x, y) crosses row len(x) // 2.

    Fills the table row by row, keeping two rows of distances and, from the
    middle row on, two rows that record for every cell the column at which
    its optimal path crossed the middle row.
    """
    m = len(y)
    mid = len(x) // 2
    sub = sub_rows(y)
    prev = list(range(0, (m + 1) * C_INS, C_INS))
    for i in range(1, mid + 1):
        row_sub = sub[x[i - 1]]
        cur = [i * C_DEL] * (m + 1)
        for j in range(1, m + 1):
            best = prev[j - 1] + row_sub[j - 1]
            up = prev[j] + C_DEL
            if up < best:
                best = up
            left = cur[j - 1] + C_INS
            if left < best:
                best = left
            cur[j] = best
        prev = cur
    cross_prev = list(range(m + 1))  # on the middle row, a cell crosses at its own column
    for i in range(mid + 1, len(x) + 1):
        row_sub = sub[x[i - 1]]
        cur = [i * C_DEL] * (m + 1)
        cross = [0] * (m + 1)
        for j in range(1, m + 1):
            best = prev[j - 1] + row_sub[j - 1]
            origin = cross_prev[j - 1]
            up = prev[j] + C_DEL
            if up < best:
                best = up
                origin = cross_prev[j]
            left = cur[j - 1] + C_INS
            if left < best:
                best = left
                origin = cross[j - 1]
            cur[j] = best
            cross[j] = origin
        prev, cross_prev = cur, cross
    return cross_prev[m]


def _align_letter(a, y):
    """Best alignment of the one-letter word a with the non-empty word y."""
    k = min(range(len(y)), key=lambda j: sub_cost(a, y[j]))
    if sub_cost(a, y[k]) <= C_DEL + C_INS:
        return GAP * k + a + GAP * (len(y) - k - 1), y
    return a + GAP * len(y), GAP + y


def align_hirschberg(x, y):
    """Return (xbar, ybar), an optimal alignment of (x, y), in linear memory."""
    sys.setrecursionlimit(max(sys.getrecursionlimit(), 1000))
    parts_x, parts_y = [], []
    _solve(x, y, parts_x, parts_y)
    return "".join(parts_x), "".join(parts_y)


def _solve(x, y, out_x, out_y):
    if not y:
        out_x.append(x); out_y.append(GAP * len(x))
    elif not x:
        out_x.append(GAP * len(y)); out_y.append(y)
    elif len(x) == 1:
        xbar, ybar = _align_letter(x, y)
        out_x.append(xbar); out_y.append(ybar)
    else:
        mid = len(x) // 2
        j = cut(x, y)
        _solve(x[:mid], y[:j], out_x, out_y)
        _solve(x[mid:], y[j:], out_x, out_y)
