try:
    from data_structures.fenwick_tree import FenwickTree
except ModuleNotFoundError:
    from fenwick_tree import FenwickTree


class RangeUpdateRangeSum:
    """0-indexed range updates and range sums using two Fenwick trees."""

    def __init__(self, data: int | list[int]):
        if isinstance(data, int):
            data = [0] * data

        self.n = len(data)
        da = [0] * self.n
        prev = 0
        for i, val in enumerate(data):
            da[i] = val - prev
            prev = val

        self.ft1 = FenwickTree(da)
        self.ft2 = FenwickTree([d * i for i, d in enumerate(da)])

    def _update(self, i: int, delta: int) -> None:
        if i >= self.n:
            return

        self.ft1.update(i + 1, delta)
        self.ft2.update(i + 1, delta * i)

    # inclusive: [i, j]
    def update_range(self, i: int, j: int, delta: int) -> None:
        if i > j:
            return

        self._update(i, delta)
        self._update(j + 1, -delta)

    def query_prefix(self, i: int) -> int:
        return self.ft1.query(i + 1) * (i + 1) - self.ft2.query(i + 1)

    # inclusive: [i, j]
    def query_range(self, i: int, j: int) -> int:
        if i > j:
            return 0

        return self.query_prefix(j) - self.query_prefix(i - 1)

    def query_point(self, i: int) -> int:
        return self.query_range(i, i)


if __name__ == "__main__":
    arr = [1, 2, 3, 4, 5]
    rs = RangeUpdateRangeSum(arr)

    assert rs.query_prefix(0) == 1
    assert rs.query_prefix(4) == sum(arr)
    assert rs.query_range(1, 3) == sum(arr[1:4])
    assert rs.query_range(3, 1) == 0

    rs.update_range(1, 3, 10)
    for i in range(1, 4):
        arr[i] += 10

    assert rs.query_point(0) == arr[0]
    assert rs.query_point(2) == arr[2]
    assert rs.query_prefix(4) == sum(arr)
    assert rs.query_range(0, 4) == sum(arr)
    assert rs.query_range(1, 3) == sum(arr[1:4])

    rs.update_range(0, 4, -2)
    arr = [val - 2 for val in arr]

    assert rs.query_point(0) == arr[0]
    assert rs.query_point(4) == arr[4]
    assert rs.query_prefix(2) == sum(arr[:3])
    assert rs.query_range(2, 4) == sum(arr[2:5])

    empty = RangeUpdateRangeSum(5)
    empty.update_range(0, 2, 3)
    empty.update_range(2, 4, 5)

    assert empty.query_point(0) == 3
    assert empty.query_point(2) == 8
    assert empty.query_point(4) == 5
    assert empty.query_range(0, 4) == 24
    assert empty.query_range(1, 3) == 16

    print("All tests passed.")
