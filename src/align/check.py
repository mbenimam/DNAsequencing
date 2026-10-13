"""Independent checks on an alignment: is it valid, and what does it cost."""
from .costs import C_DEL, C_INS, GAP, sub_cost


def is_alignment(xbar, ybar, x, y):
    """True when (xbar, ybar) is an alignment of (x, y).

    Removing the gaps must give back x and y, both rows must have the same
    length, and no column may hold two gaps.
    """
    if len(xbar) != len(ybar):
        return False
    if xbar.replace(GAP, "") != x or ybar.replace(GAP, "") != y:
        return False
    return all(not (a == GAP and b == GAP) for a, b in zip(xbar, ybar))


def alignment_cost(xbar, ybar):
    """Sum of the column costs of an alignment."""
    total = 0
    for a, b in zip(xbar, ybar):
        if a == GAP:
            total += C_INS
        elif b == GAP:
            total += C_DEL
        else:
            total += sub_cost(a, b)
    return total
