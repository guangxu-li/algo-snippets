from collections.abc import Callable

log2 = [0] * (10 ** 5 + 1)
for i in range(2, 10 ** 5 + 1):
    log2[i] = log2[i // 2] + 1

class SparseTable2D:
    def __init__(self, matrix: list[list[int]], op: Callable[[int, int], int]):
        n = len(matrix)
        m = len(matrix[0]) if n else 0

        logn = log2[n]
        logm = log2[m]

        st = [[[[0] * m for _ in range(n)] for _ in range(logm + 1)] for _ in range(logn + 1)]
        st[0][0] = [row.copy() for row in matrix]

        for kc in range(1, logm + 1):
            full = 1 << kc
            half = full >> 1

            for i in range(n):
                for j in range(m - full + 1):
                    st[0][kc][i][j] = op(st[0][kc - 1][i][j], st[0][kc - 1][i][j + half])

        for kr in range(1, logn + 1):
            fullr = 1 << kr
            halfr = fullr >> 1
            for kc in range(logm + 1):
                fullc = 1 << kc
                for i in range(n - fullr + 1):
                    for j in range(m - fullc + 1):
                        st[kr][kc][i][j] = op(st[kr - 1][kc][i][j], st[kr - 1][kc][i + halfr][j])

        self.st = st
        self.op = op

    def query(self, r1: int, c1: int, r2: int, c2: int) -> int:
        kr = log2[r2 - r1 + 1]
        kc = log2[c2 - c1 + 1]

        return self.op(
            self.op(self.st[kr][kc][r1][c1], self.st[kr][kc][r2 - (1 << kr) + 1][c2 - (1 << kc) + 1]),
            self.op(self.st[kr][kc][r2 - (1 << kr) + 1][c1], self.st[kr][kc][r1][c2 - (1 << kc) + 1]),
        )


# ===================================================================


import random
from math import gcd
from typing import Callable, List


def brute_force_query(
    grid: List[List[int]],
    r1: int,
    c1: int,
    r2: int,
    c2: int,
    op: Callable[[int, int], int],
) -> int:
    ans = grid[r1][c1]

    for r in range(r1, r2 + 1):
        for c in range(c1, c2 + 1):
            ans = op(ans, grid[r][c])

    return ans


def test_fixed_min() -> None:
    grid = [
        [5, 2, 4, 7],
        [1, 3, 6, 8],
        [9, 0, 2, 4],
    ]

    st = SparseTable2D(grid, min)

    assert st.query(0, 0, 0, 0) == 5
    assert st.query(0, 0, 0, 3) == 2
    assert st.query(0, 0, 2, 0) == 1
    assert st.query(0, 0, 2, 2) == 0
    assert st.query(1, 1, 2, 3) == 0
    assert st.query(0, 2, 2, 3) == 2
    assert st.query(0, 0, 2, 3) == 0


def test_fixed_max() -> None:
    grid = [
        [5, 2, 4, 7],
        [1, 3, 6, 8],
        [9, 0, 2, 4],
    ]

    st = SparseTable2D(grid, max)

    assert st.query(0, 0, 0, 0) == 5
    assert st.query(0, 0, 0, 3) == 7
    assert st.query(0, 0, 2, 0) == 9
    assert st.query(0, 0, 2, 2) == 9
    assert st.query(1, 1, 2, 3) == 8
    assert st.query(0, 2, 2, 3) == 8
    assert st.query(0, 0, 2, 3) == 9


def test_fixed_gcd() -> None:
    grid = [
        [12, 18, 24],
        [30, 36, 42],
        [48, 54, 60],
    ]

    st = SparseTable2D(grid, gcd)

    assert st.query(0, 0, 0, 0) == 12
    assert st.query(0, 0, 0, 2) == 6
    assert st.query(0, 0, 2, 0) == 6
    assert st.query(0, 0, 2, 2) == 6
    assert st.query(1, 1, 2, 2) == 6


def test_single_row() -> None:
    grid = [[4, 1, 7, 3, 9]]

    st = SparseTable2D(grid, min)

    assert st.query(0, 0, 0, 0) == 4
    assert st.query(0, 1, 0, 3) == 1
    assert st.query(0, 2, 0, 4) == 3
    assert st.query(0, 0, 0, 4) == 1


def test_single_column() -> None:
    grid = [
        [4],
        [1],
        [7],
        [3],
        [9],
    ]

    st = SparseTable2D(grid, min)

    assert st.query(0, 0, 0, 0) == 4
    assert st.query(1, 0, 3, 0) == 1
    assert st.query(2, 0, 4, 0) == 3
    assert st.query(0, 0, 4, 0) == 1


def test_one_cell_matrix() -> None:
    grid = [[42]]

    st_min = SparseTable2D(grid, min)
    st_max = SparseTable2D(grid, max)
    st_gcd = SparseTable2D(grid, gcd)

    assert st_min.query(0, 0, 0, 0) == 42
    assert st_max.query(0, 0, 0, 0) == 42
    assert st_gcd.query(0, 0, 0, 0) == 42


def test_negative_numbers() -> None:
    grid = [
        [-5, -2, -4],
        [-1, -3, -6],
        [-9, 0, -2],
    ]

    st_min = SparseTable2D(grid, min)
    st_max = SparseTable2D(grid, max)

    assert st_min.query(0, 0, 2, 2) == -9
    assert st_min.query(0, 1, 1, 2) == -6
    assert st_max.query(0, 0, 2, 2) == 0
    assert st_max.query(0, 0, 1, 1) == -1


def test_random_min_against_bruteforce() -> None:
    random.seed(0)

    for _ in range(100):
        n = random.randint(1, 8)
        m = random.randint(1, 8)

        grid = [
            [random.randint(-100, 100) for _ in range(m)]
            for _ in range(n)
        ]

        st = SparseTable2D(grid, min)

        for _ in range(100):
            r1 = random.randint(0, n - 1)
            r2 = random.randint(r1, n - 1)
            c1 = random.randint(0, m - 1)
            c2 = random.randint(c1, m - 1)

            expected = brute_force_query(grid, r1, c1, r2, c2, min)
            actual = st.query(r1, c1, r2, c2)

            assert actual == expected


def test_random_max_against_bruteforce() -> None:
    random.seed(1)

    for _ in range(100):
        n = random.randint(1, 8)
        m = random.randint(1, 8)

        grid = [
            [random.randint(-100, 100) for _ in range(m)]
            for _ in range(n)
        ]

        st = SparseTable2D(grid, max)

        for _ in range(100):
            r1 = random.randint(0, n - 1)
            r2 = random.randint(r1, n - 1)
            c1 = random.randint(0, m - 1)
            c2 = random.randint(c1, m - 1)

            expected = brute_force_query(grid, r1, c1, r2, c2, max)
            actual = st.query(r1, c1, r2, c2)

            assert actual == expected


def test_random_gcd_against_bruteforce() -> None:
    random.seed(2)

    for _ in range(100):
        n = random.randint(1, 8)
        m = random.randint(1, 8)

        grid = [
            [random.randint(1, 100) for _ in range(m)]
            for _ in range(n)
        ]

        st = SparseTable2D(grid, gcd)

        for _ in range(100):
            r1 = random.randint(0, n - 1)
            r2 = random.randint(r1, n - 1)
            c1 = random.randint(0, m - 1)
            c2 = random.randint(c1, m - 1)

            expected = brute_force_query(grid, r1, c1, r2, c2, gcd)
            actual = st.query(r1, c1, r2, c2)

            assert actual == expected

if __name__ == "__main__":
    test_fixed_min()
    test_fixed_max()
    test_fixed_gcd()
    test_single_row()
    test_single_column()
    test_one_cell_matrix()
    test_negative_numbers()
    test_random_min_against_bruteforce()
    test_random_max_against_bruteforce()
    test_random_gcd_against_bruteforce()

    print("All tests passed.")
