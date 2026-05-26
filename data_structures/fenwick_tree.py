class FenwickTree:
    """1-indexed Fenwick tree for point updates and prefix sums."""

    def __init__(self, data: int | list[int]):
        if isinstance(data, int):
            self.n = data
            self.ft = [0] * (self.n + 1)
            return

        self.n = len(data)
        self.ft = [0] + data[:]

        for i in range(1, self.n + 1):
            j = i + (i & -i)
            if j <= self.n:
                self.ft[j] += self.ft[i]

    def update(self, i: int, delta: int) -> None:
        while i <= self.n:
            self.ft[i] += delta
            i += i & -i

    def query(self, i: int) -> int:
        total = 0
        while i > 0:
            total += self.ft[i]
            i -= i & -i
        return total

    def query_prefix(self, i: int) -> int:
        return self.query(i)

    # inclusive: [i, j]
    def query_range(self, i: int, j: int) -> int:
        if i > j:
            return 0
        return self.query(j) - self.query(i - 1)

    # same range query as above, but combines the two prefix walks
    def query_range2(self, i: int, j: int) -> int:
        if i > j:
            return 0

        total = 0
        i -= 1

        while j > 0:
            total += self.ft[j]
            j -= j & -j

        while i > 0:
            total -= self.ft[i]
            i -= i & -i

        return total

    # lower_bound find the smallest index with prefix >= target
    def lower_bound(self, target: int) -> int:
        total, i = 0, 0
        for step in reversed(range(self.n.bit_length())):
            ni = i + (1 << step)
            if ni <= self.n and total + self.ft[ni] < target:
                total += self.ft[ni]
                i = ni
        return i + 1

    # smallest index with prefix > target
    def upper_bound(self, target: int) -> int:
        total, i = 0, 0
        for step in reversed(range(self.n.bit_length())):
            ni = i + (1 << step)
            if ni <= self.n and total + self.ft[ni] <= target:
                total += self.ft[ni]
                i = ni
        return i + 1

    def lower_bound2(self, target: int) -> int:
        lo, hi = 1, self.n + 1
        while lo < hi:
            mid = (lo + hi) >> 1
            val = self.query(mid)
            if val < target:
                lo = mid + 1
            else:
                hi = mid

        return lo

    def upper_bound2(self, target: int) -> int:
        lo, hi = 1, self.n + 1
        while lo < hi:
            mid = (lo + hi) >> 1
            val = self.query(mid)
            if val <= target:
                lo = mid + 1
            else:
                hi = mid

        return lo


if __name__ == "__main__":
    arr = [1, 2, 3, 4, 5]
    ft = FenwickTree(arr)

    assert ft.query(1) == 1
    assert ft.query(5) == sum(arr)
    assert ft.query_prefix(3) == 6
    assert ft.query_prefix(5) == sum(arr)
    assert ft.query_range(2, 4) == 9
    assert ft.query_range2(2, 4) == 9
    assert ft.query_range(4, 2) == 0
    assert ft.query_range2(4, 2) == 0

    ft.update(3, 10)
    arr[2] += 10

    assert ft.query(3) == sum(arr[:3])
    assert ft.query_prefix(5) == sum(arr)
    assert ft.query_range(2, 4) == sum(arr[1:4])
    assert ft.query_range2(2, 4) == sum(arr[1:4])

    for target in range(1, sum(arr) + 1):
        expected_lower = next(
            i for i in range(1, len(arr) + 1) if sum(arr[:i]) >= target
        )
        expected_upper = next(
            (i for i in range(1, len(arr) + 1) if sum(arr[:i]) > target),
            len(arr) + 1,
        )

        assert ft.lower_bound(target) == expected_lower
        assert ft.lower_bound2(target) == expected_lower
        assert ft.upper_bound(target) == expected_upper
        assert ft.upper_bound2(target) == expected_upper

    empty = FenwickTree(3)
    empty.update(1, 4)
    empty.update(3, 6)

    assert empty.query_prefix(3) == 10
    assert empty.query_range(2, 3) == 6
    assert empty.query_range2(2, 3) == 6

    print("All tests passed.")
