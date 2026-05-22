class SparseTableSecondMinMax:
    def __init__(self, arr: list[int]):
        if not arr:
            raise ValueError("arr must be non-empty")

        self.arr = arr
        self.n = len(arr)

        self.log2 = [0] * (self.n + 1)
        for i in range(2, self.n + 1):
            self.log2[i] = self.log2[i // 2] + 1

        self.m = self.log2[self.n] + 1

        # min_st[k][i] = (minimum_index, second_minimum_index)
        # max_st[k][i] = (maximum_index, second_maximum_index)
        self.min_st = [[(-1, -1)] * self.n for _ in range(self.m)]
        self.max_st = [[(-1, -1)] * self.n for _ in range(self.m)]

        for i in range(self.n):
            self.min_st[0][i] = (i, -1)
            self.max_st[0][i] = (i, -1)

        for k in range(1, self.m):
            full = 1 << k
            half = full >> 1

            for i in range(self.n - full + 1):
                self.min_st[k][i] = self._merge_min(
                    self.min_st[k - 1][i],
                    self.min_st[k - 1][i + half],
                )

                self.max_st[k][i] = self._merge_max(
                    self.max_st[k - 1][i],
                    self.max_st[k - 1][i + half],
                )

    def _check_bounds(self, lo: int, hi: int) -> None:
        if not (0 <= lo <= hi < self.n):
            raise IndexError(f"invalid range [{lo}, {hi}] for n={self.n}")

    def _merge_min(self, a: tuple[int, int], b: tuple[int, int]) -> tuple[int, int]:
        candidates = [a[0], a[1], b[0], b[1]]

        # Deduplicate by index because sparse table queries use overlapping blocks.
        candidates = list({idx for idx in candidates if idx != -1})

        candidates.sort(key=lambda idx: (self.arr[idx], idx))

        first = candidates[0]
        second = candidates[1] if len(candidates) >= 2 else -1

        return first, second

    def _merge_max(self, a: tuple[int, int], b: tuple[int, int]) -> tuple[int, int]:
        candidates = [a[0], a[1], b[0], b[1]]

        # Deduplicate by index because sparse table queries use overlapping blocks.
        candidates = list({idx for idx in candidates if idx != -1})

        candidates.sort(key=lambda idx: (-self.arr[idx], idx))

        first = candidates[0]
        second = candidates[1] if len(candidates) >= 2 else -1

        return first, second

    def query_min_indices(self, lo: int, hi: int) -> tuple[int, int]:
        self._check_bounds(lo, hi)

        k = self.log2[hi - lo + 1]

        left = self.min_st[k][lo]
        right = self.min_st[k][hi - (1 << k) + 1]

        return self._merge_min(left, right)

    def query_max_indices(self, lo: int, hi: int) -> tuple[int, int]:
        self._check_bounds(lo, hi)

        k = self.log2[hi - lo + 1]

        left = self.max_st[k][lo]
        right = self.max_st[k][hi - (1 << k) + 1]

        return self._merge_max(left, right)

    def query_min_index(self, lo: int, hi: int) -> int:
        first, _ = self.query_min_indices(lo, hi)
        return first

    def query_second_min_index(self, lo: int, hi: int) -> int:
        _, second = self.query_min_indices(lo, hi)
        return second

    def query_max_index(self, lo: int, hi: int) -> int:
        first, _ = self.query_max_indices(lo, hi)
        return first

    def query_second_max_index(self, lo: int, hi: int) -> int:
        _, second = self.query_max_indices(lo, hi)
        return second

    def query_min(self, lo: int, hi: int) -> int:
        return self.arr[self.query_min_index(lo, hi)]

    def query_second_min(self, lo: int, hi: int) -> int | None:
        idx = self.query_second_min_index(lo, hi)
        return None if idx == -1 else self.arr[idx]

    def query_max(self, lo: int, hi: int) -> int:
        return self.arr[self.query_max_index(lo, hi)]

    def query_second_max(self, lo: int, hi: int) -> int | None:
        idx = self.query_second_max_index(lo, hi)
        return None if idx == -1 else self.arr[idx]


if __name__ == "__main__":
    import random

    def brute_min_indices(arr: list[int], lo: int, hi: int) -> tuple[int, int]:
        ids = list(range(lo, hi + 1))
        ids.sort(key=lambda idx: (arr[idx], idx))

        first = ids[0]
        second = ids[1] if len(ids) >= 2 else -1

        return first, second

    def brute_max_indices(arr: list[int], lo: int, hi: int) -> tuple[int, int]:
        ids = list(range(lo, hi + 1))
        ids.sort(key=lambda idx: (-arr[idx], idx))

        first = ids[0]
        second = ids[1] if len(ids) >= 2 else -1

        return first, second

    # Basic test
    arr = [5, 2, 7, 2, 9, 1]
    st = SparseTableSecondMinMax(arr)

    assert st.query_min_indices(0, 5) == (5, 1)
    assert st.query_min(0, 5) == 1
    assert st.query_second_min(0, 5) == 2

    assert st.query_max_indices(0, 5) == (4, 2)
    assert st.query_max(0, 5) == 9
    assert st.query_second_max(0, 5) == 7

    # Duplicate values test
    arr = [2, 2, 2]
    st = SparseTableSecondMinMax(arr)

    assert st.query_min_indices(0, 2) == (0, 1)
    assert st.query_second_min(0, 2) == 2

    assert st.query_max_indices(0, 2) == (0, 1)
    assert st.query_second_max(0, 2) == 2

    # Single element range test
    arr = [10, 5, 7]
    st = SparseTableSecondMinMax(arr)

    assert st.query_min_index(1, 1) == 1
    assert st.query_second_min_index(1, 1) == -1
    assert st.query_second_min(1, 1) is None

    assert st.query_max_index(1, 1) == 1
    assert st.query_second_max_index(1, 1) == -1
    assert st.query_second_max(1, 1) is None

    # Negative numbers
    arr = [-5, -1, -10, 3, 0]
    st = SparseTableSecondMinMax(arr)

    assert st.query_min_indices(0, 4) == (2, 0)
    assert st.query_second_min(0, 4) == -5

    assert st.query_max_indices(0, 4) == (3, 4)
    assert st.query_second_max(0, 4) == 0

    # Exhaustive fixed test
    arr = [4, 1, 3, 1, 5, 9, 2, 6]
    st = SparseTableSecondMinMax(arr)

    for lo in range(len(arr)):
        for hi in range(lo, len(arr)):
            assert st.query_min_indices(lo, hi) == brute_min_indices(arr, lo, hi)
            assert st.query_max_indices(lo, hi) == brute_max_indices(arr, lo, hi)

    # Random brute-force tests
    for _ in range(1000):
        n = random.randint(1, 100)
        arr = [random.randint(-20, 20) for _ in range(n)]

        st = SparseTableSecondMinMax(arr)

        for lo in range(n):
            for hi in range(lo, n):
                expected_min = brute_min_indices(arr, lo, hi)
                expected_max = brute_max_indices(arr, lo, hi)

                got_min = st.query_min_indices(lo, hi)
                got_max = st.query_max_indices(lo, hi)

                assert got_min == expected_min, {
                    "arr": arr,
                    "lo": lo,
                    "hi": hi,
                    "got": got_min,
                    "expected": expected_min,
                }

                assert got_max == expected_max, {
                    "arr": arr,
                    "lo": lo,
                    "hi": hi,
                    "got": got_max,
                    "expected": expected_max,
                }

                min_idx, second_min_idx = got_min
                max_idx, second_max_idx = got_max

                assert st.query_min(lo, hi) == arr[min_idx]
                assert st.query_max(lo, hi) == arr[max_idx]

                if second_min_idx == -1:
                    assert st.query_second_min(lo, hi) is None
                else:
                    assert st.query_second_min(lo, hi) == arr[second_min_idx]

                if second_max_idx == -1:
                    assert st.query_second_max(lo, hi) is None
                else:
                    assert st.query_second_max(lo, hi) == arr[second_max_idx]

    print("All tests passed!")
