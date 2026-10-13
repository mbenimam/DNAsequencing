"""The cost model: what each edit operation costs."""

GAP = "-"
C_INS = 2  # a gap in the first sequence: a letter of y is inserted
C_DEL = 2  # a gap in the second sequence: a letter of x is deleted
C_SUB_PAIR = 3  # A<->T or G<->C
C_SUB_OTHER = 4

_PAIRS = {("A", "T"), ("T", "A"), ("G", "C"), ("C", "G")}


def sub_cost(a, b):
    """Cost of replacing letter a by letter b (0 when they are equal)."""
    if a == b:
        return 0
    return C_SUB_PAIR if (a, b) in _PAIRS else C_SUB_OTHER


def sub_rows(y):
    """For each letter a, the list of sub_cost(a, y[j]) for every j.

    The inner loops of the table-filling functions read one of these lists
    instead of calling sub_cost once per cell.
    """
    return {a: [sub_cost(a, b) for b in y] for a in "ACGT"}
