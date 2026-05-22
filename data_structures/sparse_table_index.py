from collections.abc import Callable

log2 = [0] * (10**5 + 1)
for i in range(2, 10**5+1):
    log2[i] = log2[i//2] + 1


class SparseTableIndex:
    def __init__(self, arr: list[int], op: Callable[[int, int], int] = min):
        if not arr:
            raise ValueError("arr must be non-empty")

        self.arr = arr
        self.n = len(arr)

        n = self.n
        m = log2[n] + 1

        st = [[0] * n for _ in range(m)]
        st[0] = list(range(n))

        for k in range(1, m):
            full = 1 << k
            half = full >> 1

            for i in range(n - full + 1):
                left = st[k - 1][i]
                right = st[k - 1][i + half]

                st[k][i] = left if op(arr[left], arr[right]) == arr[left] else right

        self.m = m
        self.st = st
        self.op = op

    def query_index(self, lo: int, hi: int) -> int:
        k = log2[hi - lo + 1]

        left = self.st[k][lo]
        right = self.st[k][hi - (1 << k) + 1]

        return left if self.op(arr[left], arr[right]) == arr[left] else right

    def query(self, lo: int, hi: int) -> int:
        return self.arr[self.query_index(lo, hi)]


if __name__ == "__main__":
    import random

    # Basic min tests
    arr = [1, 3, 2, 7, 9, 11]
    st = SparseTableIndex(arr)
    assert st.query(1, 4) == 2
    assert st.query(0, 2) == 1
    assert st.query(0, 5) == 1
    assert st.query(3, 3) == 7

    # Max tests
    arr = [5, 1, 9, 3, 7, 2]
    st = SparseTableIndex(arr, op=max)
    assert st.query(0, 5) == 9
    assert st.query(1, 3) == 9
    assert st.query(3, 5) == 7
    assert st.query(4, 4) == 7

    # Negative numbers
    arr = [-5, -1, -10, 3, 0]
    st = SparseTableIndex(arr, op=min)
    assert st.query(0, 4) == -10
    assert st.query(0, 1) == -5
    assert st.query(3, 4) == 0

    st = SparseTableIndex(arr, op=max)
    assert st.query(0, 4) == 3
    assert st.query(0, 2) == -1
    assert st.query(2, 2) == -10

    # Single element
    arr = [42]
    st = SparseTableIndex(arr)
    assert st.query(0, 0) == 42

    # Exhaustive brute-force tests for min
    arr = [random.randint(-100, 100) for _ in range(50)]
    st = SparseTableIndex(arr, op=min)

    for lo in range(len(arr)):
        for hi in range(lo, len(arr)):
            expected = min(arr[lo:hi + 1])
            assert st.query(lo, hi) == expected

    # Exhaustive brute-force tests for max
    arr = [random.randint(-100, 100) for _ in range(50)]
    st = SparseTableIndex(arr, op=max)

    for lo in range(len(arr)):
        for hi in range(lo, len(arr)):
            expected = max(arr[lo:hi + 1])
            assert st.query(lo, hi) == expected

    print("All tests passed!")
