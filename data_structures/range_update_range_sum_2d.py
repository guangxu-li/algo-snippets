try:
    from data_structures.fenwick_tree_2d import FenwickTree2D
except ModuleNotFoundError:
    from fenwick_tree_2d import FenwickTree2D


class RangeUpdateRangeSum2D:
    def __init__(self, matrix: list[list[int]]):
        m = len(matrix)
        n = len(matrix[0]) if m else 0

        da = [[0] * n for _ in range(m)]

        for i in range(m):
            for j in range(n):
                top = matrix[i - 1][j] if i else 0
                left = matrix[i][j - 1] if j else 0
                topleft = matrix[i - 1][j - 1] if i and j else 0
                da[i][j] = matrix[i][j] - top - left + topleft

        self.m = m
        self.n = n
        self.ft00 = FenwickTree2D(da)  # ft00 da[i][j]
        self.ft01 = FenwickTree2D(
            [[j * val for j, val in enumerate(row)] for row in da]
        )  # ft01 j*da[i][j]
        self.ft10 = FenwickTree2D(
            [[i * val for val in row] for i, row in enumerate(da)]
        )  # ft10 i*da[i][j]
        self.ft11 = FenwickTree2D(
            [[i * j * val for j, val in enumerate(row)] for i, row in enumerate(da)]
        )  # ft11 i*j*da[i][j]

    def _update(self, r: int, c: int, delta: int) -> None:
        r, c = max(0, r), max(0, c)

        if r >= self.m or c >= self.n:
            return

        self.ft00.update(r + 1, c + 1, delta)
        self.ft01.update(r + 1, c + 1, delta * c)
        self.ft10.update(r + 1, c + 1, delta * r)
        self.ft11.update(r + 1, c + 1, delta * r * c)

    def update_range(self, r1: int, c1: int, r2: int, c2: int, delta: int) -> None:
        r1, c1 = max(0, r1), max(0, c1)
        r2, c2 = min(self.m - 1, r2), min(self.n - 1, c2)

        if r1 > r2 or c1 > c2:
            return

        self._update(r1, c1, delta)
        self._update(r1, c2 + 1, -delta)
        self._update(r2 + 1, c1, -delta)
        self._update(r2 + 1, c2 + 1, delta)

    def query_prefix(self, r: int, c: int) -> int:
        return (
            (r + 1) * (c + 1) * self.ft00.query(r + 1, c + 1)
            - (r + 1) * self.ft01.query(r + 1, c + 1)
            - (c + 1) * self.ft10.query(r + 1, c + 1)
            + self.ft11.query(r + 1, c + 1)
        )

    def query_range(self, r1: int, c1: int, r2: int, c2: int) -> int:
        r1, c1 = max(0, r1), max(0, c1)
        r2, c2 = min(self.m - 1, r2), min(self.n - 1, c2)

        if r1 > r2 or c1 > c2:
            return 0

        return (
            self.query_prefix(r2, c2)
            - self.query_prefix(r2, c1 - 1)
            - self.query_prefix(r1 - 1, c2)
            + self.query_prefix(r1 - 1, c1 - 1)
        )

    def query_point(self, r: int, c: int) -> int:
        return self.query_range(r, c, r, c)


if __name__ == "__main__":
    import random

    # All coordinates are 0-indexed.

    # Basic 3x3 matrix
    matrix = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ]
    ru = RangeUpdateRangeSum2D(matrix)

    # query_point recovers original cells
    for r in range(3):
        for c in range(3):
            assert ru.query_point(r, c) == matrix[r][c]

    # query_range on various rectangles
    assert ru.query_range(0, 0, 2, 2) == 45
    assert ru.query_range(0, 0, 1, 1) == 12  # 1+2+4+5
    assert ru.query_range(1, 1, 2, 2) == 28  # 5+6+8+9
    assert ru.query_range(0, 1, 0, 2) == 5  # 2+3
    assert ru.query_range(2, 0, 2, 2) == 24  # 7+8+9
    assert ru.query_range(0, 0, 2, 0) == 12  # 1+4+7

    # query_prefix matches query_range from (0,0)
    assert ru.query_prefix(0, 0) == 1
    assert ru.query_prefix(1, 1) == 12
    assert ru.query_prefix(2, 2) == 45

    # query_range with r1=0 / c1=0 hits the negative-index branch of query_prefix
    assert ru.query_range(0, 0, 0, 0) == 1
    assert ru.query_range(0, 0, 2, 0) == 12

    # Range update on a 2x2 sub-rectangle
    ru.update_range(0, 0, 1, 1, 5)
    # Matrix becomes:
    #  6  7 3
    #  9 10 6
    #  7  8 9
    assert ru.query_point(0, 0) == 6
    assert ru.query_point(0, 1) == 7
    assert ru.query_point(0, 2) == 3
    assert ru.query_point(1, 0) == 9
    assert ru.query_point(1, 1) == 10
    assert ru.query_point(1, 2) == 6
    assert ru.query_point(2, 0) == 7
    assert ru.query_range(0, 0, 2, 2) == 45 + 5 * 4

    # Undo with negative delta
    ru.update_range(0, 0, 1, 1, -5)
    assert ru.query_range(0, 0, 2, 2) == 45
    for r in range(3):
        for c in range(3):
            assert ru.query_point(r, c) == matrix[r][c]

    # Full-grid range update
    ru.update_range(0, 0, 2, 2, 100)
    for r in range(3):
        for c in range(3):
            assert ru.query_point(r, c) == matrix[r][c] + 100
    ru.update_range(0, 0, 2, 2, -100)
    assert ru.query_range(0, 0, 2, 2) == 45

    # Overlapping range updates compose
    ru.update_range(0, 0, 1, 1, 1)
    ru.update_range(1, 1, 2, 2, 2)
    # (1,1) is in both rectangles -> +1+2 = +3
    assert ru.query_point(1, 1) == 5 + 3
    assert ru.query_point(0, 0) == 1 + 1
    assert ru.query_point(2, 2) == 9 + 2
    assert ru.query_point(0, 2) == 3  # untouched
    ru.update_range(0, 0, 1, 1, -1)
    ru.update_range(1, 1, 2, 2, -2)
    assert ru.query_range(0, 0, 2, 2) == 45

    # Degenerate rectangles (r1 > r2 or c1 > c2) are no-ops
    ru.update_range(2, 0, 0, 0, 99)
    ru.update_range(0, 2, 0, 0, 99)
    assert ru.query_range(0, 0, 2, 2) == 45

    # Out-of-bounds (high end) clips to in-bounds
    ru.update_range(0, 0, 10, 10, 1)
    for r in range(3):
        for c in range(3):
            assert ru.query_point(r, c) == matrix[r][c] + 1
    ru.update_range(0, 0, 10, 10, -1)
    assert ru.query_range(0, 0, 2, 2) == 45

    # Out-of-bounds (negative) clips to (0, 0)
    ru.update_range(-5, -5, 1, 1, 1)
    for r in range(2):
        for c in range(2):
            assert ru.query_point(r, c) == matrix[r][c] + 1
    assert ru.query_point(0, 2) == matrix[0][2]
    ru.update_range(-5, -5, 1, 1, -1)
    assert ru.query_range(0, 0, 2, 2) == 45

    # query_range clamps to in-bounds and returns 0 for degenerate rectangles
    assert ru.query_range(0, 0, 10, 10) == 45  # high end clipped
    assert ru.query_range(-5, -5, 10, 10) == 45  # both ends clipped
    assert ru.query_range(-5, -5, 0, 0) == 1  # clipped to (0,0,0,0)
    assert ru.query_range(5, 5, 10, 10) == 0  # entirely past the matrix
    assert ru.query_range(-5, -5, -1, -1) == 0  # entirely before the matrix
    assert ru.query_range(2, 0, 0, 2) == 0  # degenerate (r1 > r2)
    assert ru.query_range(0, 2, 2, 0) == 0  # degenerate (c1 > c2)
    assert ru.query_point(10, 10) == 0  # query_point inherits clamping

    # Single-row matrix
    ru_row = RangeUpdateRangeSum2D([[1, 2, 3, 4]])
    assert ru_row.query_range(0, 0, 0, 3) == 10
    ru_row.update_range(0, 1, 0, 2, 5)
    assert ru_row.query_point(0, 0) == 1
    assert ru_row.query_point(0, 1) == 7
    assert ru_row.query_point(0, 2) == 8
    assert ru_row.query_point(0, 3) == 4

    # Single-column matrix
    ru_col = RangeUpdateRangeSum2D([[1], [2], [3], [4]])
    assert ru_col.query_range(0, 0, 3, 0) == 10
    ru_col.update_range(1, 0, 2, 0, 5)
    assert ru_col.query_point(0, 0) == 1
    assert ru_col.query_point(1, 0) == 7
    assert ru_col.query_point(2, 0) == 8
    assert ru_col.query_point(3, 0) == 4

    # 1x1 matrix
    ru_one = RangeUpdateRangeSum2D([[42]])
    assert ru_one.query_point(0, 0) == 42
    ru_one.update_range(0, 0, 0, 0, 8)
    assert ru_one.query_point(0, 0) == 50
    ru_one.update_range(0, 0, 0, 0, -50)
    assert ru_one.query_point(0, 0) == 0

    # update(r, c, delta) is a difference-array primitive:
    # it adds delta to every cell (i, j) with i >= r and j >= c.
    # (Used internally by update_range; not a matrix point update.)
    ru_diff = RangeUpdateRangeSum2D([[0] * 3 for _ in range(3)])
    ru_diff._update(1, 1, 5)
    for r in range(3):
        for c in range(3):
            expected = 5 if r >= 1 and c >= 1 else 0
            assert ru_diff.query_point(r, c) == expected

    # Brute-force comparison on a non-square matrix
    def brute_range(grid: list[list[int]], r1: int, c1: int, r2: int, c2: int) -> int:
        return sum(grid[r][c] for r in range(r1, r2 + 1) for c in range(c1, c2 + 1))

    random.seed(42)
    m, n = 5, 7
    init = [[random.randint(-10, 10) for _ in range(n)] for _ in range(m)]
    ru = RangeUpdateRangeSum2D(init)
    brute = [row[:] for row in init]

    # Initial state: every rectangle matches
    for r1 in range(m):
        for c1 in range(n):
            for r2 in range(r1, m):
                for c2 in range(c1, n):
                    assert ru.query_range(r1, c1, r2, c2) == brute_range(
                        brute, r1, c1, r2, c2
                    )

    # Interleave random rectangle updates and queries
    for _ in range(60):
        r1 = random.randint(0, m - 1)
        r2 = random.randint(r1, m - 1)
        c1 = random.randint(0, n - 1)
        c2 = random.randint(c1, n - 1)
        delta = random.randint(-20, 20)
        ru.update_range(r1, c1, r2, c2, delta)
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                brute[r][c] += delta

        qr1 = random.randint(0, m - 1)
        qr2 = random.randint(qr1, m - 1)
        qc1 = random.randint(0, n - 1)
        qc2 = random.randint(qc1, n - 1)
        assert ru.query_range(qr1, qc1, qr2, qc2) == brute_range(
            brute, qr1, qc1, qr2, qc2
        )

    # Final exhaustive check
    for r1 in range(m):
        for c1 in range(n):
            for r2 in range(r1, m):
                for c2 in range(c1, n):
                    assert ru.query_range(r1, c1, r2, c2) == brute_range(
                        brute, r1, c1, r2, c2
                    )
    for r in range(m):
        for c in range(n):
            assert ru.query_point(r, c) == brute[r][c]

    print("All tests passed.")
