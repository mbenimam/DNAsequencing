import glob
import os
import random

import pytest

from align import (C_DEL, C_INS, GAP, align_dp, align_hirschberg, alignment_cost, cut, dist_naive,
                   dist_table, dist_two_rows, is_alignment, read_instance, sub_cost, traceback)

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
KNOWN = {"Inst_0000010_44.adn": 10, "Inst_0000010_7.adn": 8, "Inst_0000010_8.adn": 2}


def table_distance(x, y):
    return dist_table(x, y)[len(x)][len(y)]


def random_pairs(count, max_len, seed):
    rng = random.Random(seed)
    for _ in range(count):
        yield ("".join(rng.choice("ACGT") for _ in range(rng.randint(0, max_len))),
               "".join(rng.choice("ACGT") for _ in range(rng.randint(0, max_len))))


def test_cost_model():
    assert sub_cost("A", "A") == 0
    assert sub_cost("A", "T") == sub_cost("T", "A") == sub_cost("G", "C") == sub_cost("C", "G") == 3
    assert sub_cost("A", "G") == sub_cost("C", "T") == 4
    assert alignment_cost("AT-TGTA", "ATCT-TA") == C_INS + C_DEL == 4


def test_read_instance():
    x, y = read_instance(os.path.join(DATA, "Inst_0000010_44.adn"))
    assert (x, y) == ("TATATGAGTC", "TATTT")


def test_is_alignment_rules():
    assert is_alignment("AT-TGTA", "ATCT-TA", "ATTGTA", "ATCTTA")
    assert not is_alignment("AT-TGTA", "ATCTTA", "ATTGTA", "ATCTTA")       # different lengths
    assert not is_alignment("A-T", "A-T", "AT", "AT")                      # a column of two gaps
    assert not is_alignment("AT-TGTA", "ATCT-TA", "ATTGTT", "ATCTTA")      # does not spell x


@pytest.mark.parametrize("name,expected", KNOWN.items())
def test_known_distances(name, expected):
    x, y = read_instance(os.path.join(DATA, name))
    assert dist_naive(x, y) == expected
    assert table_distance(x, y) == expected
    assert dist_two_rows(x, y) == expected
    assert align_dp(x, y)[0] == expected
    assert alignment_cost(*align_hirschberg(x, y)) == expected


def test_worked_example():
    x, y = "ATTGTA", "ATCTTA"
    table = dist_table(x, y)
    assert [list(r) for r in table][3] == [6, 4, 2, 4, 2, 4, 6]
    assert table[6][6] == 4
    assert cut(x, y) == 4


def test_edge_cases():
    assert table_distance("", "") == dist_two_rows("", "") == dist_naive("", "") == 0
    assert table_distance("ACG", "") == dist_two_rows("ACG", "") == 3 * C_DEL
    assert table_distance("", "ACG") == dist_two_rows("", "ACG") == 3 * C_INS
    assert align_dp("", "AC") == (4, "--", "AC")
    assert align_hirschberg("AC", "") == ("AC", "--")
    assert align_hirschberg("", "") == ("", "")
    assert align_hirschberg("A", "A") == ("A", "A")
    assert alignment_cost(*align_hirschberg("A", "TTTT")) == 3 + 3 * C_INS


def test_every_method_agrees_with_enumeration():
    for x, y in random_pairs(300, 7, seed=1):
        d = dist_naive(x, y)
        assert table_distance(x, y) == d, (x, y)
        assert dist_two_rows(x, y) == d, (x, y)


def test_alignments_are_valid_and_optimal():
    for x, y in random_pairs(400, 40, seed=2):
        d = dist_two_rows(x, y)
        for xbar, ybar in (traceback(x, y, dist_table(x, y)), align_hirschberg(x, y)):
            assert is_alignment(xbar, ybar, x, y), (x, y, xbar, ybar)
            assert alignment_cost(xbar, ybar) == d, (x, y, xbar, ybar)


def test_cut_splits_into_two_optimal_halves():
    for x, y in random_pairs(300, 30, seed=3):
        if len(x) < 2 or not y:
            continue
        mid, j = len(x) // 2, cut(x, y)
        assert dist_two_rows(x[:mid], y[:j]) + dist_two_rows(x[mid:], y[j:]) == dist_two_rows(x, y), (x, y)


def test_distance_is_symmetric_with_these_costs():
    for x, y in random_pairs(100, 30, seed=4):
        assert dist_two_rows(x, y) == dist_two_rows(y, x)


def test_medium_instances_agree():
    for path in sorted(glob.glob(os.path.join(DATA, "Inst_00005*.adn"))):
        x, y = read_instance(path)
        d = dist_two_rows(x, y)
        assert table_distance(x, y) == d
        xbar, ybar = align_hirschberg(x, y)
        assert is_alignment(xbar, ybar, x, y) and alignment_cost(xbar, ybar) == d
        assert GAP not in x and GAP not in y
