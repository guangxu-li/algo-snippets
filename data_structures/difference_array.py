from itertools import accumulate


class DifferenceArray:
    """0-indexed difference array for range updates and point queries."""

    def __init__(self, arr: int | list[int]):
        if isinstance(arr, int):
            arr = [0] * arr

        self.n = len(arr)
        self.da = [0] * self.n
        prev = 0
        for i, val in enumerate(arr):
            self.da[i] = val - prev
            prev = val

    def update(self, i: int, delta: int) -> None:
        if i < self.n:
            self.da[i] += delta

    # inclusive: [i, j]
    def update_range(self, i: int, j: int, delta: int) -> None:
        if i > j:
            return

        self.update(i, delta)
        self.update(j + 1, -delta)

    def query_point(self, i: int) -> int:
        return sum(self.da[: i + 1])

    def build(self) -> list[int]:
        return list(accumulate(self.da))


if __name__ == "__main__":
    da = DifferenceArray(5)
    da.update_range(1, 3, 2)
    da.update_range(2, 4, 3)

    assert da.query_point(0) == 0
    assert da.query_point(1) == 2
    assert da.query_point(2) == 5
    assert da.query_point(3) == 5
    assert da.query_point(4) == 3
    assert da.build() == [0, 2, 5, 5, 3]

    base = [1, 2, 4, 8]
    da = DifferenceArray(base)
    assert da.build() == base

    da.update_range(0, 1, 10)
    da.update_range(3, 3, -3)
    da.update_range(2, 1, 99)

    assert da.query_point(0) == 11
    assert da.query_point(1) == 12
    assert da.query_point(2) == 4
    assert da.query_point(3) == 5
    assert da.build() == [11, 12, 4, 5]

    print("All tests passed.")
