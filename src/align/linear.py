"""Edit distance in linear memory: only the previous row of the table is kept."""
from .costs import C_DEL, C_INS, sub_rows


def last_row(x, y):
    """The last row of the table: distance(x, y[:j]) for every j."""
    m = len(y)
    sub = sub_rows(y)
    prev = list(range(0, (m + 1) * C_INS, C_INS))
    for i, a in enumerate(x, 1):
        row_sub = sub[a]
        cur = [i * C_DEL] * (m + 1)
        left = cur[0]
        for j in range(1, m + 1):
            best = prev[j - 1] + row_sub[j - 1]
            up = prev[j] + C_DEL
            if up < best:
                best = up
            left += C_INS
            if left < best:
                best = left
            else:
                left = best
            cur[j] = best
        prev = cur
    return prev


def dist_two_rows(x, y):
    """Edit distance from x to y, in memory proportional to len(y)."""
    return last_row(x, y)[len(y)]
