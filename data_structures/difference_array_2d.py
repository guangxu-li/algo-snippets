class DifferenceArray2D:
    """0-indexed 2D difference array for rectangle updates."""

    def __init__(self, matrix: list[list[int]]) -> None:
        self.m = len(matrix)
        self.n = len(matrix[0]) if self.m else 0

        self.da = [[0] * (self.n + 1) for _ in range(self.m + 1)]
        for r in range(self.m):
            for c in range(self.n):
                v = matrix[r][c]
                if r:
                    v -= matrix[r - 1][c]
                if c:
                    v -= matrix[r][c - 1]
                if r and c:
                    v += matrix[r - 1][c - 1]
                self.da[r][c] = v

        # Equivalent two-pass form: row-wise 1D diff, then column-wise 1D diff.
        # row_diff = [[0] * self.n for _ in range(self.m)]
        # for r in range(self.m):
        #     for c in range(self.n):
        #         row_diff[r][c] = matrix[r][c] - (matrix[r][c - 1] if c else 0)
        # for r in range(self.m):
        #     for c in range(self.n):
        #         self.da[r][c] = row_diff[r][c] - (row_diff[r - 1][c] if r else 0)

    # inclusive: rows [r1, r2], cols [c1, c2]
    def update_range(self, r1: int, c1: int, r2: int, c2: int, delta: int) -> None:
        if r1 > r2 or c1 > c2:
            return

        self.da[r1][c1] += delta
        self.da[r2 + 1][c1] -= delta
        self.da[r1][c2 + 1] -= delta
        self.da[r2 + 1][c2 + 1] += delta

    def build(self) -> list[list[int]]:
        ps = [[0] * (self.n + 1) for _ in range(self.m + 1)]
        for r in range(self.m):
            for c in range(self.n):
                ps[r + 1][c + 1] = (
                    self.da[r][c] + ps[r][c + 1] + ps[r + 1][c] - ps[r][c]
                )
        return [row[1:] for row in ps[1:]]


def _zeros(m: int, n: int) -> list[list[int]]:
    return [[0] * n for _ in range(m)]


if __name__ == "__main__":
    import random

    # Single-cell update
    da = DifferenceArray2D(_zeros(3, 3))
    da.update_range(1, 1, 1, 1, 5)
    assert da.build() == [
        [0, 0, 0],
        [0, 5, 0],
        [0, 0, 0],
    ]

    # Full-grid update
    da = DifferenceArray2D(_zeros(2, 2))
    da.update_range(0, 0, 1, 1, 3)
    assert da.build() == [[3, 3], [3, 3]]

    # Overlapping rectangles
    da = DifferenceArray2D(_zeros(3, 4))
    da.update_range(0, 0, 1, 1, 1)
    da.update_range(1, 1, 2, 2, 2)
    assert da.build() == [
        [1, 1, 0, 0],
        [1, 3, 2, 0],
        [0, 2, 2, 0],
    ]

    # Negative deltas
    da = DifferenceArray2D(_zeros(2, 2))
    da.update_range(0, 0, 1, 1, 5)
    da.update_range(0, 0, 0, 0, -2)
    assert da.build() == [[3, 5], [5, 5]]

    # Degenerate rectangles (r1 > r2 or c1 > c2) are no-ops
    da = DifferenceArray2D(_zeros(2, 2))
    da.update_range(1, 1, 0, 0, 99)
    da.update_range(0, 1, 1, 0, 99)
    assert da.build() == [[0, 0], [0, 0]]

    # Edge-touching rectangles
    da = DifferenceArray2D(_zeros(3, 3))
    da.update_range(0, 0, 2, 0, 1)
    da.update_range(0, 0, 0, 2, 1)
    da.update_range(2, 0, 2, 2, 1)
    da.update_range(0, 2, 2, 2, 1)
    assert da.build() == [
        [2, 1, 2],
        [1, 0, 1],
        [2, 1, 2],
    ]

    # Single-row grid
    da = DifferenceArray2D(_zeros(1, 5))
    da.update_range(0, 1, 0, 3, 7)
    assert da.build() == [[0, 7, 7, 7, 0]]

    # Single-column grid
    da = DifferenceArray2D(_zeros(5, 1))
    da.update_range(1, 0, 3, 0, 4)
    assert da.build() == [[0], [4], [4], [4], [0]]

    # 1x1 grid
    da = DifferenceArray2D(_zeros(1, 1))
    da.update_range(0, 0, 0, 0, 42)
    assert da.build() == [[42]]

    # build() is pure: repeated calls return the same result
    da = DifferenceArray2D(_zeros(3, 3))
    da.update_range(0, 0, 2, 2, 1)
    da.update_range(1, 1, 1, 1, 1)
    first = da.build()
    second = da.build()
    assert (
        first
        == second
        == [
            [1, 1, 1],
            [1, 2, 1],
            [1, 1, 1],
        ]
    )

    # Initialize from an existing 2D grid
    grid = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ]
    da = DifferenceArray2D(grid)
    assert da.build() == grid

    # Updates compose with initial grid values
    da = DifferenceArray2D([[1, 1], [1, 1]])
    da.update_range(0, 0, 1, 1, 10)
    assert da.build() == [[11, 11], [11, 11]]

    # Empty grid
    da = DifferenceArray2D([])
    assert da.build() == []

    # Brute-force comparison: random initial grid plus random rectangle updates
    random.seed(42)
    m, n = 7, 6
    grid = [[random.randint(-10, 10) for _ in range(n)] for _ in range(m)]
    da = DifferenceArray2D(grid)
    brute = [row[:] for row in grid]
    for _ in range(50):
        r1 = random.randint(0, m - 1)
        r2 = random.randint(r1, m - 1)
        c1 = random.randint(0, n - 1)
        c2 = random.randint(c1, n - 1)
        delta = random.randint(-10, 10)
        da.update_range(r1, c1, r2, c2, delta)
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                brute[r][c] += delta
    assert da.build() == brute

    print("All tests passed.")
