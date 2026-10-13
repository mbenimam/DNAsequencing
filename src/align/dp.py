"""Dynamic programming with the full table: distance, then one optimal alignment."""
from array import array

from .costs import C_DEL, C_INS, GAP, sub_cost, sub_rows


def dist_table(x, y):
    """The (len(x)+1) x (len(y)+1) table D, with D[i][j] = distance(x[:i], y[:j])."""
    m = len(y)
    sub = sub_rows(y)
    prev = list(range(0, (m + 1) * C_INS, C_INS))
    table = [array("i", prev)]
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
        table.append(array("i", cur))
        prev = cur
    return table


def traceback(x, y, table):
    """Walk from the last cell back to D[0][0] and return one optimal alignment."""
    xbar, ybar = [], []
    i, j = len(x), len(y)
    while i > 0 or j > 0:
        here = table[i][j]
        if i > 0 and j > 0 and here == table[i - 1][j - 1] + sub_cost(x[i - 1], y[j - 1]):
            xbar.append(x[i - 1]); ybar.append(y[j - 1])
            i -= 1; j -= 1
        elif i > 0 and here == table[i - 1][j] + C_DEL:
            xbar.append(x[i - 1]); ybar.append(GAP)
            i -= 1
        else:
            xbar.append(GAP); ybar.append(y[j - 1])
            j -= 1
    return "".join(reversed(xbar)), "".join(reversed(ybar))


def align_dp(x, y):
    """Return (distance, xbar, ybar) using the full table."""
    table = dist_table(x, y)
    xbar, ybar = traceback(x, y, table)
    return table[len(x)][len(y)], xbar, ybar
