class PrefixSum2D:
    def __init__(self, matrix: list[list[int]]):
        self.m = len(matrix)
        self.n = len(matrix[0]) if self.m else 0

        self.ps = [[0] * (self.n + 1) for _ in range(self.m + 1)]
        for i in range(self.m):
            for j in range(self.n):
                self.ps[i + 1][j + 1] = matrix[i][j] + self.ps[i + 1][j] + self.ps[i][j + 1] - self.ps[i][j]

    def query(self, r1: int, c1: int, r2: int, c2: int) -> int:
        r1, c1 = max(0, r1), max(0, c1)
        r2, c2 = min(self.m - 1, r2), min(self.n - 1, c2)

        if r1 > r2 or c1 > c2:
            return 0

        return self.ps[r2 + 1][c2 + 1] - self.ps[r2 + 1][c1] - self.ps[r1][c2 + 1] + self.ps[r1][c1]


if __name__ == "__main__":
    # Basic matrix
    matrix = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ]

    ps = PrefixSum2D(matrix)

    # Single cell queries
    assert ps.query(0, 0, 0, 0) == 1
    assert ps.query(1, 1, 1, 1) == 5
    assert ps.query(2, 2, 2, 2) == 9

    # Row queries
    assert ps.query(0, 0, 0, 2) == 6      # 1 + 2 + 3
    assert ps.query(1, 0, 1, 2) == 15     # 4 + 5 + 6
    assert ps.query(2, 0, 2, 2) == 24     # 7 + 8 + 9

    # Column queries
    assert ps.query(0, 0, 2, 0) == 12     # 1 + 4 + 7
    assert ps.query(0, 1, 2, 1) == 15     # 2 + 5 + 8
    assert ps.query(0, 2, 2, 2) == 18     # 3 + 6 + 9

    # Submatrix queries
    assert ps.query(0, 0, 1, 1) == 12     # 1 + 2 + 4 + 5
    assert ps.query(1, 1, 2, 2) == 28     # 5 + 6 + 8 + 9
    assert ps.query(0, 1, 2, 2) == 33     # 2 + 3 + 5 + 6 + 8 + 9

    # Whole matrix
    assert ps.query(0, 0, 2, 2) == 45

    # Out-of-bound queries should be clipped
    assert ps.query(-1, -1, 1, 1) == 12   # clipped to (0,0) -> (1,1)
    assert ps.query(1, 1, 10, 10) == 28   # clipped to (1,1) -> (2,2)
    assert ps.query(-10, -10, 10, 10) == 45

    # Completely invalid/outside queries
    assert ps.query(3, 0, 5, 2) == 0
    assert ps.query(0, 3, 2, 5) == 0
    assert ps.query(2, 2, 1, 1) == 0

    # Matrix with negative numbers
    matrix2 = [
        [1, -2, 3],
        [-4, 5, -6],
        [7, -8, 9],
    ]

    ps2 = PrefixSum2D(matrix2)

    assert ps2.query(0, 0, 2, 2) == 5
    assert ps2.query(0, 0, 1, 1) == 0     # 1 - 2 - 4 + 5
    assert ps2.query(1, 1, 2, 2) == 0     # 5 - 6 - 8 + 9
    assert ps2.query(0, 1, 2, 1) == -5    # -2 + 5 - 8

    # Single row
    matrix3 = [[1, 2, 3, 4]]
    ps3 = PrefixSum2D(matrix3)

    assert ps3.query(0, 0, 0, 3) == 10
    assert ps3.query(0, 1, 0, 2) == 5
    assert ps3.query(-1, -1, 10, 10) == 10

    # Single column
    matrix4 = [
        [1],
        [2],
        [3],
        [4],
    ]

    ps4 = PrefixSum2D(matrix4)

    assert ps4.query(0, 0, 3, 0) == 10
    assert ps4.query(1, 0, 2, 0) == 5
    assert ps4.query(-1, -1, 10, 10) == 10

    # Empty matrix
    matrix5: list[list[int]] = []
    ps5 = PrefixSum2D(matrix5)

    assert ps5.query(0, 0, 0, 0) == 0
    assert ps5.query(-10, -10, 10, 10) == 0

    print("All tests passed.")
