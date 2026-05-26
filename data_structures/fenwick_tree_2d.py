class FenwickTree2D:
    def __init__(self, matrix: list[list[int]]):
        m = len(matrix)
        n = len(matrix[0]) if m else 0

        ft = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                ft[i][j] += matrix[i - 1][j - 1]
                ni, nj = i+(i&-i), j+(j&-j)

                if ni <= m:
                    ft[ni][j] += ft[i][j]
                if nj <= n:
                    ft[i][nj] += ft[i][j]
                if ni <= m and nj <= n:
                    ft[ni][nj] -= ft[i][j]

        # Equivalent O(m * n) linear-time build with three pass
        # ft = [[0] * (n + 1) for _ in range(m + 1)]
        # # 1. Copy initial values
        # for i in range(1, m + 1):
        #     for j in range(1, n + 1):
        #         ft[i][j] = matrix[i - 1][j - 1]
        # # 2. Propagate horizontally (row by row)
        # for i in range(1, m + 1):
        #     for j in range(1, n + 1):
        #         if j + (j&-j) <= n:
        #             ft[i][j + (j&-j)] += ft[i][j]
        # # 3. Propagate vertically (col by col)
        # for i in range(1, m + 1):
        #     for j in range(1, n + 1):
        #         if i + (i&-i) <= m:
        #             ft[i + (i&-i)][j] += ft[i][j]

        self.m = m
        self.n = n
        self.ft = ft

    def update(self, i: int, j: int, val: int) -> None:
        while i <= self.m:
            j1 = j
            while j1 <= self.n:
                self.ft[i][j1] += val
                j1 += j1&-j1
            i += i&-i

    def query(self, i: int, j: int) -> int:
        total = 0
        while i > 0:
            j1 = j
            while j1 > 0:
                total += self.ft[i][j1]
                j1 -= j1&-j1
            i -= i&-i
        return total

    def query_range(self, r1: int, c1: int, r2: int, c2: int) -> int:
        return self.query(r2, c2) - self.query(r2, c1 - 1) - self.query(r1 - 1, c2) + self.query(r1 - 1, c1 - 1)


if __name__ == "__main__":
    import random

    # All coordinates are 1-indexed.

    # Basic 3x3 matrix
    matrix = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ]
    ft = FenwickTree2D(matrix)

    # Single-cell queries
    assert ft.query_range(1, 1, 1, 1) == 1
    assert ft.query_range(2, 2, 2, 2) == 5
    assert ft.query_range(3, 3, 3, 3) == 9

    # Row queries
    assert ft.query_range(1, 1, 1, 3) == 6    # 1+2+3
    assert ft.query_range(2, 1, 2, 3) == 15   # 4+5+6
    assert ft.query_range(3, 1, 3, 3) == 24   # 7+8+9

    # Column queries
    assert ft.query_range(1, 1, 3, 1) == 12   # 1+4+7
    assert ft.query_range(1, 2, 3, 2) == 15   # 2+5+8
    assert ft.query_range(1, 3, 3, 3) == 18   # 3+6+9

    # Sub-rectangles
    assert ft.query_range(1, 1, 2, 2) == 12   # 1+2+4+5
    assert ft.query_range(2, 2, 3, 3) == 28   # 5+6+8+9
    assert ft.query_range(1, 2, 3, 3) == 33   # 2+3+5+6+8+9

    # Whole matrix
    assert ft.query_range(1, 1, 3, 3) == 45

    # Prefix queries (via query directly)
    assert ft.query(1, 1) == 1
    assert ft.query(2, 2) == 12               # 1+2+4+5
    assert ft.query(3, 2) == 27               # 1+2+4+5+7+8
    assert ft.query(3, 3) == 45

    # Prefix with zero row/col is 0 (sentinel behavior)
    assert ft.query(0, 3) == 0
    assert ft.query(3, 0) == 0
    assert ft.query(0, 0) == 0

    # Point updates are additive
    ft.update(2, 2, 10)                       # cell (2,2): 5 -> 15
    assert ft.query_range(2, 2, 2, 2) == 15
    assert ft.query_range(1, 1, 3, 3) == 55
    assert ft.query_range(2, 2, 3, 3) == 38   # 15+6+8+9

    ft.update(2, 2, -10)                      # back to 5
    assert ft.query_range(1, 1, 3, 3) == 45

    # Repeated updates on the same cell compose
    ft.update(1, 1, 100)
    ft.update(1, 1, -50)
    assert ft.query_range(1, 1, 1, 1) == 51   # 1 + 100 - 50
    ft.update(1, 1, -51)                      # restore
    assert ft.query_range(1, 1, 1, 1) == 0
    ft.update(1, 1, 1)

    # Negative values in initial matrix
    matrix2 = [
        [1, -2, 3],
        [-4, 5, -6],
        [7, -8, 9],
    ]
    ft2 = FenwickTree2D(matrix2)
    assert ft2.query_range(1, 1, 3, 3) == 5
    assert ft2.query_range(1, 1, 2, 2) == 0   # 1 - 2 - 4 + 5
    assert ft2.query_range(2, 2, 3, 3) == 0   # 5 - 6 - 8 + 9
    assert ft2.query_range(1, 2, 3, 2) == -5  # -2 + 5 - 8

    # Single-row matrix
    ft3 = FenwickTree2D([[1, 2, 3, 4]])
    assert ft3.query_range(1, 1, 1, 4) == 10
    assert ft3.query_range(1, 2, 1, 3) == 5
    ft3.update(1, 3, 7)
    assert ft3.query_range(1, 1, 1, 4) == 17

    # Single-column matrix
    ft4 = FenwickTree2D([[1], [2], [3], [4]])
    assert ft4.query_range(1, 1, 4, 1) == 10
    assert ft4.query_range(2, 1, 3, 1) == 5
    ft4.update(3, 1, 7)
    assert ft4.query_range(1, 1, 4, 1) == 17

    # 1x1 matrix
    ft5 = FenwickTree2D([[42]])
    assert ft5.query_range(1, 1, 1, 1) == 42
    ft5.update(1, 1, 8)
    assert ft5.query_range(1, 1, 1, 1) == 50
    ft5.update(1, 1, -50)
    assert ft5.query_range(1, 1, 1, 1) == 0

    # Empty matrix: no rows / no cols -> query at origin sentinel is 0
    ft_empty = FenwickTree2D([])
    assert ft_empty.query(0, 0) == 0
    assert ft_empty.m == 0 and ft_empty.n == 0

    # Building from zeros then updating equals building directly
    values = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ]
    direct = FenwickTree2D(values)
    incremental = FenwickTree2D([[0] * 3 for _ in range(3)])
    for r in range(3):
        for c in range(3):
            incremental.update(r + 1, c + 1, values[r][c])
    for r1 in range(1, 4):
        for c1 in range(1, 4):
            for r2 in range(r1, 4):
                for c2 in range(c1, 4):
                    assert direct.query_range(r1, c1, r2, c2) == incremental.query_range(r1, c1, r2, c2)

    # Brute-force comparison on a non-square matrix
    def brute_range(mat: list[list[int]], r1: int, c1: int, r2: int, c2: int) -> int:
        return sum(mat[r][c] for r in range(r1, r2 + 1) for c in range(c1, c2 + 1))

    random.seed(123)
    m, n = 6, 5
    matrix = [[random.randint(-10, 10) for _ in range(n)] for _ in range(m)]
    ft = FenwickTree2D(matrix)

    for r1 in range(m):
        for c1 in range(n):
            for r2 in range(r1, m):
                for c2 in range(c1, n):
                    got = ft.query_range(r1 + 1, c1 + 1, r2 + 1, c2 + 1)
                    want = brute_range(matrix, r1, c1, r2, c2)
                    assert got == want, (r1, c1, r2, c2, got, want)

    # Interleave random point updates and queries
    for _ in range(50):
        i = random.randint(1, m)
        j = random.randint(1, n)
        delta = random.randint(-20, 20)
        ft.update(i, j, delta)
        matrix[i - 1][j - 1] += delta

        r1 = random.randint(0, m - 1)
        r2 = random.randint(r1, m - 1)
        c1 = random.randint(0, n - 1)
        c2 = random.randint(c1, n - 1)
        assert ft.query_range(r1 + 1, c1 + 1, r2 + 1, c2 + 1) == brute_range(matrix, r1, c1, r2, c2)

    # After all updates, every rectangle still matches brute force
    for r1 in range(m):
        for c1 in range(n):
            for r2 in range(r1, m):
                for c2 in range(c1, n):
                    assert ft.query_range(r1 + 1, c1 + 1, r2 + 1, c2 + 1) == brute_range(matrix, r1, c1, r2, c2)

    print("All tests passed.")

    # After all updates, every rectangle still matches brute force
    for r1 in range(m):
        for c1 in range(n):
            for r2 in range(r1, m):
                for c2 in range(c1, n):
                    assert ft.query_range(
                        r1 + 1, c1 + 1, r2 + 1, c2 + 1
                    ) == brute_range(matrix, r1, c1, r2, c2)

    print("All tests passed.")
