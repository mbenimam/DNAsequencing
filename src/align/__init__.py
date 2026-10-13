"""Global alignment of two DNA sequences, four ways."""
from .costs import C_DEL, C_INS, GAP, sub_cost
from .check import alignment_cost, is_alignment
from .instance import read_instance
from .naive import dist_naive
from .dp import dist_table, traceback, align_dp
from .linear import dist_two_rows
from .hirschberg import align_hirschberg, cut

__all__ = [
    "C_DEL", "C_INS", "GAP", "sub_cost", "alignment_cost", "is_alignment", "read_instance",
    "dist_naive", "dist_table", "traceback", "align_dp", "dist_two_rows", "align_hirschberg", "cut",
]
