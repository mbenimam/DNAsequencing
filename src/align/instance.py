"""Reading an instance file: two lengths, then two sequences of spaced letters."""


def read_instance(path):
    """Return (x, y) as two strings."""
    with open(path) as f:
        n = int(f.readline())
        m = int(f.readline())
        x = "".join(f.readline().split())
        y = "".join(f.readline().split())
    if len(x) != n or len(y) != m:
        raise ValueError(f"{path}: header says {n} and {m} letters, found {len(x)} and {len(y)}")
    return x, y
